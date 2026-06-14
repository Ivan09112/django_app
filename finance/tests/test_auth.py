from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.register_url = reverse('finance:register')
        self.login_url = reverse('finance:login')
        # В Django LogoutView по умолчанию работает по методу POST
        self.logout_url = reverse('finance:logout')
        self.user = User.objects.create_user(username='existinguser', password='password123')

    def test_register_page_loads(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')

    def test_successful_registration(self):
        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        })
        self.assertEqual(response.status_code, 302) # Редирект на дашборд
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_registration_validation_user_exists(self):
        response = self.client.post(self.register_url, {
            'username': 'existinguser',
            'email': 'existing@example.com',
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        })
        self.assertEqual(response.status_code, 200) # Возвращает форму с ошибкой
        self.assertContains(response, 'Имя пользователя уже занято.')

    def test_registration_validation_passwords_mismatch(self):
        response = self.client.post(self.register_url, {
            'username': 'anotheruser',
            'email': 'anotheruser@example.com',
            'password': 'password123',
            'password_confirm': 'differentpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Пароли не совпадают.')

    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_successful_login(self):
        response = self.client.post(self.login_url, {
            'username': 'existinguser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)

    def test_dashboard_page_loads_for_authenticated_user(self):
        self.client.login(username='existinguser', password='password123')
        # Создадим категорию, чтобы избежать ошибок при рендеринге пустого списка
        from finance.models import Category
        Category.objects.create(user=self.user, name='Тест', type='EXPENSE')
        response = self.client.get(reverse('finance:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'finance/dashboard.html')
