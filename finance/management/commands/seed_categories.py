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
            {'name': 'Продукты и кафе', 'icon': 'shopping-bag', 'color': '#F43F5E'},
            {'name': 'Транспорт', 'icon': 'car', 'color': '#3B82F6'},
            {'name': 'Жилье и комм. услуги', 'icon': 'home', 'color': '#F59E0B'},
            {'name': 'Развлечения', 'icon': 'film', 'color': '#8B5CF6'},
            {'name': 'Покупки', 'icon': 'gift', 'color': '#EC4899'},
            {'name': 'Здоровье', 'icon': 'heart', 'color': '#10B981'},
        ]
        
        income_cats = [
            {'name': 'Зарплата', 'icon': 'briefcase', 'color': '#10B981'},
            {'name': 'Фриланс', 'icon': 'globe', 'color': '#06B6D4'},
            {'name': 'Инвестиции', 'icon': 'trending-up', 'color': '#84CC16'},
            {'name': 'Подарки и прочее', 'icon': 'coins', 'color': '#EAB308'},
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
            {'amount': '5000.00', 'type': 'INCOME', 'category': 'Зарплата', 'date': today - datetime.timedelta(days=5), 'description': 'Ежемесячная зарплата'},
            {'amount': '850.00', 'type': 'INCOME', 'category': 'Фриланс', 'date': today - datetime.timedelta(days=2), 'description': 'Дизайн веб-сайта (проект)'},
            
            # Расходы
            {'amount': '1200.00', 'type': 'EXPENSE', 'category': 'Жилье и комм. услуги', 'date': today - datetime.timedelta(days=5), 'description': 'Аренда квартиры'},
            {'amount': '95.50', 'type': 'EXPENSE', 'category': 'Жилье и комм. услуги', 'date': today - datetime.timedelta(days=4), 'description': 'Счет за электричество'},
            {'amount': '154.20', 'type': 'EXPENSE', 'category': 'Продукты и кафе', 'date': today - datetime.timedelta(days=4), 'description': 'Еженедельные продукты в Spar'},
            {'amount': '45.00', 'type': 'EXPENSE', 'category': 'Транспорт', 'date': today - datetime.timedelta(days=3), 'description': 'Заправка автомобиля'},
            {'amount': '85.00', 'type': 'EXPENSE', 'category': 'Продукты и кафе', 'date': today - datetime.timedelta(days=2), 'description': 'Ужин с друзьями'},
            {'amount': '120.00', 'type': 'EXPENSE', 'category': 'Покупки', 'date': today - datetime.timedelta(days=2), 'description': 'Новые кроссовки'},
            {'amount': '30.00', 'type': 'EXPENSE', 'category': 'Развлечения', 'date': today - datetime.timedelta(days=1), 'description': 'Билеты в кино'},
            {'amount': '15.00', 'type': 'EXPENSE', 'category': 'Развлечения', 'date': today, 'description': 'Подписка на Netflix'},
            {'amount': '18.50', 'type': 'EXPENSE', 'category': 'Транспорт', 'date': today, 'description': 'Поездка на такси (Uber)'},
            {'amount': '60.00', 'type': 'EXPENSE', 'category': 'Здоровье', 'date': today, 'description': 'Абонемент в спортзал'},
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

