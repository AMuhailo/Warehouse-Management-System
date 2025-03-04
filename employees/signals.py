from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.core.mail import send_mail
from .models import Profile
from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_save, sender = User)
def profile_create(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user = instance)


