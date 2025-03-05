from django.contrib import admin
from .models import Goods, Provider, Category
# Register your models here.

admin.site.register(Category)

@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ['title','quantity','price','in_stock','category','provider','imported','added','updated']
    list_filter = ['category','in_stock','provider','added','updated']
    list_editable = ['price','in_stock']
    date_hierarchy = 'added'
    prepopulated_fields = {'slug':('title',)}
    
@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name','location','agent','email','number']
    search_fields = ['name','number']