from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from management.models import Goods, Status
from orders.models import  Order, OrderItem
from management.tasks import replenish_goods
# Create your views here.

def create_order(request):
    cart = request.session.get('cart', {})
    if not cart:
        return JsonResponse({"error":"Empty cart"}, status = 400)
    
    status_ad = Status.objects.get(name = 'AD')
    status_ms = Status.objects.get(name = 'MS')
    order = Order.objects.create(statuc = 'expected')
    for goods_id , quantity in cart.items():
        good = get_object_or_404(Goods, id = goods_id)
        
        if good.decrease(quantity, status_ad, status_ms):
            OrderItem.objects.create(order, good, quantity)
            if good.quantity <= 5:
                replenish_goods.delay(good.id )
                
        else:
            return JsonResponse({"error":f"Not enough {good.title} in stock"})
    request.session['cart'] = {}
    
    return JsonResponse({"message":'Order created', 'order_id':order.id})