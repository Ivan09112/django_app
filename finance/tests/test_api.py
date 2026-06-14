from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from finance.models import Category, Transaction
from decimal import Decimal
import datetime
import json

class FinanceAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='password123')
        self.client.login(username='apiuser', password='password123')
        self.category = Category.objects.create(
            user=self.user,
            name='Food',
            type='EXPENSE',
            icon='shopping-bag',
            color='#FF0000'
        )
        self.add_url = reverse('finance:api_add_transaction')

    def test_add_transaction_api(self):
        response = self.client.post(self.add_url, {
            'amount': '45.00',
            'type': 'EXPENSE',
            'category': self.category.id,
            'date': '2026-06-14',
            'description': 'Groceries'
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['transaction']['amount'], '45.00')
        self.assertTrue(Transaction.objects.filter(description='Groceries').exists())

    def test_delete_transaction_api(self):
        tx = Transaction.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('20.00'),
            type='EXPENSE',
            date=datetime.date.today(),
            description='Bus ticket'
        )
        delete_url = reverse('finance:api_delete_transaction', args=[tx.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertFalse(Transaction.objects.filter(id=tx.id).exists())
