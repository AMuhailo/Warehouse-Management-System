from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from management.models import Provider
from employees.models import Manager
from .models import Goods
from django.db.models import Q


User = get_user_model()

@shared_task
def replenish_goods(goods_id, user):
    manager = Manager.objects.get(user=user)
    good = Goods.objects.get(id = goods_id, in_stock = (Q(True) | Q(False)))
    subject = f"Small quantity of goods { good.id }"
    message = f"There is { good.title} left in stock in the amount: { good.quantity }.Please replenish it."
    return send_mail(subject, message, 'admin@gmail.com', [manager.user.email])

@shared_task
def update_goods(good_id, quantity):
    good = Goods.objects.get(id = good_id)
    
    manager = Manager.objects.get(storage = good.city)
    subject = f"Order in store"
    message = f"Please send the product {good.title} in the amount of {quantity} pieces to the city of {good.city.city} {good.city.state} {good.city.street}. Thank you."
    return send_mail(subject, message, manager.user.email, [good.provider.email])


@shared_task
def notstock_goods(goods_id, user_id):
    manager = Manager.objects.get(id = user_id)
    goods = Goods.objects.filter(id__in = goods_id).select_related('category','city','provider')
    subject = f"Results of the day"        
    message = f"Goods that have expired after the working day {[f"\n{good.title}" for good in goods]}"
    return send_mail(subject, message, 'storage@gmail.com', [manager.user.email])