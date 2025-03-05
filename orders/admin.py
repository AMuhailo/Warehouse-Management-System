from django.contrib import admin
from orders.models import Order, OrderItem
# Register your models here.
admin.site.register(Order)
    
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order','goods','quantity']
    list_filter = ['order']
    search_fields = ['goods']
