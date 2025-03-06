from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from .models import Goods


User = get_user_model()

@shared_task
def replenish_goods(goods_id):
    good = Goods.objects.get(id = goods_id, in_stock = True)
    subject = f"Small quantity of goods { good.id }"
    message = f"There is { good.title} left in stock in the amount: { good.quantity }.Please replenish it."
    return send_mail(subject, message, 'admin@gmail.com', ['amuhailo25@gmail.com'])