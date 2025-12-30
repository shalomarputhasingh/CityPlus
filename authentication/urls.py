from django.urls import path
from . import views

urlpatterns = [
    # Citizen
    path('login/', views.login_view, name='login'), # Defaults to citizen phone login
    path('register/', views.register_view, name='register'),
    
    # Admin
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('admin-register/', views.admin_register_view, name='admin_register'),
    
    # Shared
    path('logout/', views.logout_view, name='logout'),
]
