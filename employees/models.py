from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

from management.models import Storage
# Create your models here.
class User(AbstractUser):
    is_chief = models.BooleanField(default = True)
    is_manager =  models.BooleanField(default = False)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'profiles')    
    def __str__(self):
        return f"{self.user.get_full_name()}"
    
    
class Category(models.Model):
    CATEGORY_CHOICES = (
        ('trainee', "Trainee"),
        ('loader', "Loader"),
        ('driver','Driver'),
        ('guardian','Guardian')
    )
    title = models.CharField(max_length=10, choices = CATEGORY_CHOICES, default='worker')
    organisation = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = 'category_organisation')
    
    def get_absolute_url(self):
        return reverse("model_detail", kwargs={"pk": self.pk})
    
    
    def __str__(self):
        return self.title
    
    
class Worker(models.Model):
    first_name = models.CharField(max_length = 20)
    last_name = models.CharField(max_length = 20)
    age = models.PositiveIntegerField(default = 0)
    phone = models.CharField(max_length = 20)
    storage = models.ForeignKey(Storage, on_delete = models.CASCADE, related_name = 'worker_city')
    category = models.ForeignKey(Category, on_delete = models.SET_NULL, null = True, blank = True, related_name = 'categoty_worker')
    organisation = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = 'worker_organisation')
    manager = models.ForeignKey('Manager', on_delete = models.SET_NULL, null = True, blank = True, related_name = 'worker_manager')
    
    class Meta:
        ordering = ['-id', '-age']
    
    def get_absolute_url(self):
        return reverse("emp:worder_detail_url", args=[self.pk])
    
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'manager_user')
    storage = models.OneToOneField(Storage, on_delete = models.CASCADE,related_name = 'manager_city')
    organisation = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = 'manager_organisation')

    def get_absolute_url(self):
        return reverse("emp:manager_detail_url",args=[self.pk])
    
    def __str__(self):
        return f"{self.user.first_name}"