from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='finance:landing'), name='logout'),
    path('api/transaction/add/', views.api_add_transaction, name='api_add_transaction'),
    path('api/transaction/delete/<int:tx_id>/', views.api_delete_transaction, name='api_delete_transaction'),
]
