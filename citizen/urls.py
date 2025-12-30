from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='citizen_dashboard'),
    path('submit/', views.submit_issue, name='submit_issue'),
    path('issue/<int:pk>/', views.issue_detail, name='issue_detail'),
]
