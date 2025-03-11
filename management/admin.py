from django.contrib import admin
from .models import Goods, Provider, Category, Storage, Status
# Register your models here.
@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_from', 'date_to']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','slug']
    prepopulated_fields = {"slug":('name',)}
    
    
admin.site.register(Storage)
class StorageInLine(admin.TabularInline):
    model = Storage
    fields = ['city','street','code','state']
    
@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['title','quantity','price','in_stock','category','city','provider']
    list_filter = ['category','provider']
    list_editable = ['price','in_stock']
    date_hierarchy = 'added'
    prepopulated_fields = {'slug':('title',)}
    
@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name','location','agent','email','number']
    search_fields = ['name','number']