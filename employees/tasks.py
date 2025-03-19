from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from employees.models import Manager
from management.models import Goods
from django.db.models import Q


User = get_user_model()

@shared_task
def added_to_manager(user):
    manager = Manager.objects.get(user=user)
    subject = f"Job announcement"
    message = f"You have been added to the job as a manager in the city {manager.storage.city}"
    return send_mail(subject, message, 'admin@gmail.com', [manager.user.email])

