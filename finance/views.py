from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Category, Transaction
from decimal import Decimal
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import datetime


def landing_view(request):
    if request.user.is_authenticated:
        return redirect('finance:dashboard')
    return render(request, 'finance/landing.html')

@login_required
def dashboard_view(request):
    # Получить транзакции текущего пользователя
    transactions = Transaction.objects.filter(user=request.user)
    
    # Расчет сумм
    total_income = Decimal('0.00')
    total_expense = Decimal('0.00')
    
    for t in transactions:
        if t.type == 'INCOME':
            total_income += t.amount
        else:
            total_expense += t.amount
            
    balance = total_income - total_expense
    
    # Категории для формы выбора
    categories = Category.objects.filter(Q(user=request.user) | Q(user__isnull=True))
    
    # Передача данных в контекст
    context = {
        'transactions': transactions[:15], # последние 15
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'categories': categories,
    }
    return render(request, 'finance/dashboard.html', context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect('finance:dashboard')
        
    errors = []
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not username or not password or not password_confirm:
            errors.append("Пожалуйста, заполните все обязательные поля.")
        elif password != password_confirm:
            errors.append("Пароли не совпадают.")
        elif User.objects.filter(username=username).exists():
            errors.append("Имя пользователя уже занято.")
        
        if not errors:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return redirect('finance:dashboard')
            
    return render(request, 'registration/register.html', {'errors': errors})

@login_required
@require_POST
def api_add_transaction(request):
    amount_str = request.POST.get('amount')
    tx_type = request.POST.get('type')
    category_id = request.POST.get('category')
    date_str = request.POST.get('date')
    description = request.POST.get('description', '').strip()

    if not amount_str or not tx_type or not category_id or not date_str:
        return JsonResponse({'status': 'error', 'message': 'Заполните все поля'}, status=400)

    try:
        amount = Decimal(amount_str)
        category = Category.objects.get(id=category_id)
        if category.user and category.user != request.user:
            return JsonResponse({'status': 'error', 'message': 'Неверная категория'}, status=403)
            
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        
        transaction = Transaction.objects.create(
            user=request.user,
            category=category,
            amount=amount,
            type=tx_type,
            date=date,
            description=description
        )

        all_tx = Transaction.objects.filter(user=request.user)
        total_income = sum(t.amount for t in all_tx if t.type == 'INCOME')
        total_expense = sum(t.amount for t in all_tx if t.type == 'EXPENSE')
        balance = total_income - total_expense

        return JsonResponse({
            'status': 'success',
            'transaction': {
                'id': transaction.id,
                'amount': str(transaction.amount),
                'type': transaction.type,
                'date': str(transaction.date),
                'description': transaction.description,
                'category_name': category.name,
                'category_color': category.color,
                'category_icon': category.icon
            },
            'stats': {
                'total_income': str(total_income),
                'total_expense': str(total_expense),
                'balance': str(balance)
            }
        }, status=201)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def api_delete_transaction(request, tx_id):
    try:
        transaction = Transaction.objects.get(id=tx_id, user=request.user)
        transaction.delete()

        all_tx = Transaction.objects.filter(user=request.user)
        total_income = sum(t.amount for t in all_tx if t.type == 'INCOME')
        total_expense = sum(t.amount for t in all_tx if t.type == 'EXPENSE')
        balance = total_income - total_expense

        return JsonResponse({
            'status': 'success',
            'stats': {
                'total_income': str(total_income),
                'total_expense': str(total_expense),
                'balance': str(balance)
            }
        }, status=200)
    except Transaction.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Транзакция не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)



