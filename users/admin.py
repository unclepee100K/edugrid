from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'full_name', 'email', 'is_student', 'is_teacher', 'is_admin_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('School Roles', {'fields': ('full_name', 'phone_number', 'is_student', 'is_teacher', 'is_parent', 'is_admin_staff')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)