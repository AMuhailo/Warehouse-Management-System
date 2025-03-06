from django.db import models
from django.contrib.auth.models import AbstractUser

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
        ('worker', "Worker"),
        ('manager', "Manager"),
    )
    title = models.CharField(max_length=10, choices = CATEGORY_CHOICES, default='worker')
    organisation = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = 'category_organisation')
    
    def __str__(self):
        return self.title
    
    
class Worker(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'worker_user')
    age = models.PositiveIntegerField(default = 0)
    phone = models.CharField(max_length = 20)
    city = models.CharField(max_length = 100)
    code = models.CharField(max_length=10)
    category = models.ForeignKey(Category, on_delete = models.SET_NULL, null = True, blank = True, related_name = 'categoty_worker')
    organisation = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = 'worker_organisation')
    manager = models.ForeignKey('Manager', on_delete = models.SET_NULL, null = True, blank = True, related_name = 'worker_manager')
    
    class Meta:
        ordering = ['-id', '-age']
    
    def __str__(self):
        return f"{self.user.last_name} {self.user.first_name}"


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'manager_user')
    city = models.CharField(max_length = 100)
    code = models.CharField(max_length = 10)
    organisation = models.ForeignKey(Profile, on_delete = models.CASCADE, related_name = 'manager_organisation')

    def __str__(self):
        return f"{self.user.first_name}"