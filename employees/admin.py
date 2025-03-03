from django.contrib import admin
from .models import User, Profile
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email', 'is_worker','is_manager']
    search_fields = ['username', 'first_name', 'last_name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'birthday','position']
    list_filter = ['position']