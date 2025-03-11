from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from management.models import Goods, Status
from django.db.models import Q

# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = (
        ('expected', "Expected"),
        ('completed', "Completed"),
        ('canceled', "Canceled") 
    )
    order = models.CharField(max_length=10, choices=STATUS_CHOICES, default = 'expected')
    created = models.DateTimeField(auto_now_add = True)
    
    class Meta:
        ordering = ['-created']
    
    def __str__(self):
        return f"{self.order}"
    

class OrderItem(models.Model): 
    order = models.ForeignKey(Order, on_delete = models.CASCADE, related_name = 'items')
    goods = models.ForeignKey(Goods, on_delete = models.CASCADE, related_name = 'order_goods')
    quantity = models.PositiveIntegerField()
    
    def save(self,*args, **kwargs):
        status_ad = Status.objects.get(name = 'AD')
        status_ms = Status.objects.get(name = 'MS')
        if not self.pk:
            if self.goods.decrease(self.quantity, status_ad, status_ms):
                super().save(*args, **kwargs)
            else:
                raise ValueError('Not enough goods in stock')
        else:
            super().save(*args, **kwargs)