from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, OTPVerification, LoginAttempt

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'role', 'is_registered', 'is_staff')
    list_filter = ('role', 'is_registered', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number', 'district', 'is_registered')}),
    )

admin.site.register(User, CustomUserAdmin)
admin.site.register(OTPVerification)
admin.site.register(LoginAttempt)
