from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length = 50)
    slug = models.SlugField(max_length = 60, blank = True)
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return self.name
    
    
class Goods(models.Model):
    category = models.ForeignKey(Category, on_delete = models.SET_NULL, blank = True, null = True)
    image = models.ImageField(upload_to = 'goods/', blank = True, null = True)
    title = models.CharField(max_length = 255)
    slug = models.SlugField(max_length = 255, blank = True)
    quantity = models.PositiveIntegerField(default = 0)
    price = models.DecimalField(max_digits = 10, decimal_places = 2, help_text='Unit price')
    in_stock = models.BooleanField(default = False)
    provider = models.ForeignKey('Provider', on_delete = models.SET_NULL, blank = True, null = True, related_name = 'goods_provider')

    imported = models.DateTimeField(default = timezone.now)  
    added = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    class Meta:
        ordering = ['-added','-quantity']
        indexes = [models.Index(fields=['-quantity']),
                    models.Index(fields = ['-added']),
                    models.Index(fields = ['id'])]
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
    
    def decrease(self, quantity):
        if self.quantity >= quantity:
            self.quantity -= quantity
            if self.quantity <= 0:
                self.in_stock = False
            else:
                self.in_stock = True
            self.save()
            return True
        return False
    
    def increase(self, quantity):
        self.quantity += quantity
        if self.quantity > 0:
            self.in_stock = True
        self.save()

    def full_price(self):
        return self.price * self.quantity

    def __str__(self):
        return self.title
    
class Provider(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank = True, null = True)
    agent = models.CharField(max_length=50, blank = True, null = True)
    email = models.EmailField()
    number = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name