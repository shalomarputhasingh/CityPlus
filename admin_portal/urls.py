from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='admin_dashboard'),
    
    # Verification Queue
    path('verification-queue/', views.verification_queue, name='verification_queue'),
    path('verify/<int:pk>/', views.verify_issue, name='verify_issue'),
    path('reject/<int:pk>/', views.reject_issue, name='reject_issue'),
    
    # Resolution Queue
    path('resolution-queue/', views.resolution_queue, name='resolution_queue'),
    path('solve/<int:pk>/', views.solve_issue, name='solve_issue'),
    
    # Reporting
    path('report-config/', views.report_config, name='report_config'),
    path('generate-report/', views.generate_report, name='generate_report'),
]
