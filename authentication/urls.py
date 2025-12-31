from django.urls import path
from . import views

urlpatterns = [
    # Citizen Auth Flow
    path('auth/start/', views.citizen_auth_start, name='citizen_auth_start'),
    path('verify-otp/<str:phone>/', views.verify_otp_view, name='verify_otp'),
    path('set-credentials/', views.set_credentials_view, name='set_credentials'),
    path('login/', views.citizen_login_view, name='citizen_login'),
    
    # Defaults
    path('', views.citizen_auth_start, name='login'), # Default login points to start or login
    path('register/', views.citizen_auth_start, name='register'), # Redirect to start

    # Admin
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('admin-register/', views.admin_register_view, name='admin_register'),
    
    # Shared
    path('logout/', views.logout_view, name='logout'),
]
