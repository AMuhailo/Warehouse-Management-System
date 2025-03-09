from django.contrib import admin
from .models import User, Profile, Worker, Manager, Category
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'first_name', 'last_name', 'email','is_manager']
    search_fields = ['username', 'first_name', 'last_name']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user']
    
@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name', 'age', 'phone','storage','organisation','manager']
    list_filter = ['storage','organisation','manager']
    search_fields = ['first_name']

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ['user','organisation']
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title','organisation']