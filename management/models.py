import qrcode
from io import BytesIO
from django.db import models
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from django.urls import reverse

# Create your models here.
class Status(models.Model):
    class ChoicesStatus(models.TextChoices):
        MISSING = 'MS', 'Missing'
        SEND = 'SD', 'Send'
        ARRIVED  ='AD', 'Arrived'
        
    name = models.CharField(max_length=2, choices = ChoicesStatus.choices, default = ChoicesStatus.ARRIVED)
    date_from = models.DateTimeField(blank = True, null = True)
    date_to = models.DateTimeField(blank = True, null = True)
    goods = models.ManyToManyField('Goods', related_name = 'status_goods')
    class Meta:
        ordering = ['-date_from', 'date_to']
        indexes = [models.Index(fields=['-date_from']),
                   models.Index(fields=['-date_to'])]
    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length = 50)
    slug = models.SlugField(max_length = 60, blank = True)
    
    class Meta:
        ordering = ['id']
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)
    def __str__(self):
        return self.name
    
    
class Storage(models.Model):
    city = models.CharField(max_length = 100)
    street =  models.CharField(max_length = 100, blank = True, null = True)
    code = models.PositiveIntegerField(default = 0000, blank = True, null = True)
    state = models.CharField(max_length = 100 )
    
    class Meta:
        ordering = ['-code']
        indexes = [models.Index(fields = ['-code'])]
        
    def __str__(self):
        return f"{self.city} | { self.code} | {self.street}"


class Goods(models.Model):
    category = models.ForeignKey(Category, on_delete = models.SET_NULL, blank = True, null = True)
    image = models.ImageField(upload_to = 'goods/', blank = True, null = True)
    title = models.CharField(max_length = 255)
    slug = models.SlugField(max_length = 255, blank = True)
    quantity = models.PositiveIntegerField(default = 0)
    price = models.DecimalField(max_digits = 10, decimal_places = 2, help_text='Unit price')
    in_stock = models.BooleanField(default = True)
    qr_code = models.ImageField(upload_to='qrcode/',blank = True, null = True)
    city = models.ForeignKey(Storage, on_delete = models.CASCADE, related_name = 'goods_city')
    provider = models.ForeignKey('Provider', on_delete = models.SET_NULL, blank = True, null = True, related_name = 'goods_provider')

    imported = models.DateTimeField(default = timezone.now)  
    added = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    class Meta:
        ordering = ['-added','-quantity']
        indexes = [models.Index(fields=['-quantity']),
                    models.Index(fields = ['-added']),
                    models.Index(fields = ['id'])]
        
    
    def decrease(self, quantity, status_ad, status_ms):
        if self.quantity >= quantity:
            self.quantity -= quantity
            if self.quantity <= 0:
                self.in_stock = False
                status_ad.goods.remove(self.pk)
                status_ms.goods.add(self.pk)
            else:
                self.in_stock = True
            self.save()
            return True
        return False
    
    
    def increase(self, quantity, status):
        self.quantity += quantity
        if self.quantity > 0:
            self.in_stock = False
            status.goods.remove(self.pk)
        self.save()


    def qrcode_created(self):
        qr = qrcode.make(f"http://127.0.0.1:8000/management/scan/{ self.slug }/{ self.pk}/add/")
        buffer = BytesIO()
        qr.save(buffer, format = 'PNG')
        self.qr_code.save(f"qr_{self.slug}_{self.pk}.png", ContentFile(buffer.getvalue()), save = False)
        
        
    def full_price(self):
        return self.price * self.quantity


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        self.qrcode_created()
        return super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("manage:goods_detail_url", args=[self.slug, self.pk])
    
    
    def __str__(self):
        return self.title
    
class Provider(models.Model):
    goods = models.ForeignKey(Goods, on_delete = models.SET_NULL, null = True, blank = True, related_name = 'provider_goods')
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank = True, null = True)
    agent = models.CharField(max_length=50, blank = True, null = True)
    email = models.EmailField()
    number = models.CharField(max_length=20, blank=True, null = True)
    
    
    def get_absolute_url(self):
        return reverse("manage:provider_detail_url", args=[self.name, self.id])
    
    def __str__(self):
        return self.name