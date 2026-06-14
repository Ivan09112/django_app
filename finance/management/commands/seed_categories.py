from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from finance.models import Category, Transaction
from decimal import Decimal
import datetime

class Command(BaseCommand):
    help = 'Seeds the database with default categories and a demo user with sample transactions'

    def handle(self, *args, **options):
        # Дефолтные категории расходов
        expense_cats = [
            {'name': 'Food & Dining', 'icon': 'shopping-bag', 'color': '#F43F5E'},
            {'name': 'Transport', 'icon': 'car', 'color': '#3B82F6'},
            {'name': 'Rent & Utilities', 'icon': 'home', 'color': '#F59E0B'},
            {'name': 'Entertainment', 'icon': 'film', 'color': '#8B5CF6'},
            {'name': 'Shopping', 'icon': 'gift', 'color': '#EC4899'},
            {'name': 'Health', 'icon': 'heart', 'color': '#10B981'},
        ]
        
        income_cats = [
            {'name': 'Salary', 'icon': 'briefcase', 'color': '#10B981'},
            {'name': 'Freelance', 'icon': 'globe', 'color': '#06B6D4'},
            {'name': 'Investments', 'icon': 'trending-up', 'color': '#84CC16'},
            {'name': 'Gifts/Other', 'icon': 'coins', 'color': '#EAB308'},
        ]

        # Создаем категории
        seeded_cats = {}
        for cat in expense_cats:
            db_cat, _ = Category.objects.get_or_create(
                user=None,
                name=cat['name'],
                type='EXPENSE',
                defaults={'icon': cat['icon'], 'color': cat['color']}
            )
            seeded_cats[cat['name']] = db_cat
            
        for cat in income_cats:
            db_cat, _ = Category.objects.get_or_create(
                user=None,
                name=cat['name'],
                type='INCOME',
                defaults={'icon': cat['icon'], 'color': cat['color']}
            )
            seeded_cats[cat['name']] = db_cat

        self.stdout.write(self.style.SUCCESS('Successfully seeded categories!'))

        # Создаем демо-пользователя
        username = 'demo'
        password = 'password123'
        email = 'demo@example.com'
        
        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created demo user "{username}" with password "{password}"'))
        else:
            self.stdout.write(self.style.WARNING(f'Demo user "{username}" already exists. Re-seeding transactions...'))

        # Очистим старые транзакции демо-пользователя
        Transaction.objects.filter(user=user).delete()

        # Создаем тестовые транзакции
        today = datetime.date.today()
        sample_txs = [
            # Доходы
            {'amount': '5000.00', 'type': 'INCOME', 'category': 'Salary', 'date': today - datetime.timedelta(days=5), 'description': 'Monthly Salary'},
            {'amount': '850.00', 'type': 'INCOME', 'category': 'Freelance', 'date': today - datetime.timedelta(days=2), 'description': 'Website Design Project'},
            
            # Расходы
            {'amount': '1200.00', 'type': 'EXPENSE', 'category': 'Rent & Utilities', 'date': today - datetime.timedelta(days=5), 'description': 'Apartment Rent'},
            {'amount': '95.50', 'type': 'EXPENSE', 'category': 'Rent & Utilities', 'date': today - datetime.timedelta(days=4), 'description': 'Electricity Bill'},
            {'amount': '154.20', 'type': 'EXPENSE', 'category': 'Food & Dining', 'date': today - datetime.timedelta(days=4), 'description': 'Weekly Groceries at Spar'},
            {'amount': '45.00', 'type': 'EXPENSE', 'category': 'Transport', 'date': today - datetime.timedelta(days=3), 'description': 'Gas station'},
            {'amount': '85.00', 'type': 'EXPENSE', 'category': 'Food & Dining', 'date': today - datetime.timedelta(days=2), 'description': 'Dinner with friends'},
            {'amount': '120.00', 'type': 'EXPENSE', 'category': 'Shopping', 'date': today - datetime.timedelta(days=2), 'description': 'New Sneakers'},
            {'amount': '30.00', 'type': 'EXPENSE', 'category': 'Entertainment', 'date': today - datetime.timedelta(days=1), 'description': 'Cinema tickets'},
            {'amount': '15.00', 'type': 'EXPENSE', 'category': 'Entertainment', 'date': today, 'description': 'Netflix subscription'},
            {'amount': '18.50', 'type': 'EXPENSE', 'category': 'Transport', 'date': today, 'description': 'Uber ride'},
            {'amount': '60.00', 'type': 'EXPENSE', 'category': 'Health', 'date': today, 'description': 'Gym membership'},
        ]

        for tx in sample_txs:
            Transaction.objects.create(
                user=user,
                amount=Decimal(tx['amount']),
                type=tx['type'],
                category=seeded_cats[tx['category']],
                date=tx['date'],
                description=tx['description']
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {len(sample_txs)} sample transactions for user "{username}"!'))

