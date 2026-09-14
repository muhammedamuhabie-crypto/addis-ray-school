from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets=UserAdmin.fieldsets+(('School role',{'fields':('role',)}),)
    add_fieldsets=UserAdmin.add_fieldsets+(('School role',{'fields':('role','email')}),)
