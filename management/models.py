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
    box = models.PositiveIntegerField(default=0)
    quantity = models.PositiveIntegerField(blank = True, null = True)
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    in_stock = models.BooleanField(default = False)
    provider = models.ForeignKey('Provider', on_delete = models.CASCADE, related_name = 'goods_provider')

    imported = models.DateTimeField(default = timezone.now)  
    added = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    class Meta:
        ordering = ['-added','-box']
        indexes = [models.Index(fields=['-box','-quantity']),
                    models.Index(fields = ['-added']),
                    models.Index(fields = ['id'])]
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
        
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