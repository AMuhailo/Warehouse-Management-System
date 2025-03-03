from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    is_chief = False
    is_manager = False
    is_worker = True


class Profile(models.Model):
    class PositionChoices(models.TextChoices):
        WORKER = 'WK', 'Worker'
        MANAGER = 'MG', 'Manager'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'profiles')
    image = models.FileField(upload_to = 'profile/', blank = True, null = True)
    birthday = models.PositiveIntegerField(default = 0)
    position = models.CharField(max_length=2, choices = PositionChoices , default = PositionChoices.WORKER)
    
    def __str__(self):
        return f"{self.position}: {self.user.get_full_name()}"