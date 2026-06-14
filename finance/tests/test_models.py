from django.test import TestCase
from django.contrib.auth.models import User
from finance.models import Category, Transaction
from decimal import Decimal
import datetime

class FinanceModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.category = Category.objects.create(
            user=self.user,
            name='Food',
            type='EXPENSE',
            icon='shopping-bag',
            color='#FF0000'
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Food')
        self.assertEqual(self.category.type, 'EXPENSE')
        self.assertEqual(str(self.category), 'Food (EXPENSE)')

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('150.50'),
            type='EXPENSE',
            date=datetime.date.today(),
            description='Lunch at cafe'
        )
        self.assertEqual(transaction.amount, Decimal('150.50'))
        self.assertEqual(transaction.category, self.category)
        self.assertEqual(str(transaction), f"testuser | EXPENSE | 150.50 | {datetime.date.today()}")
