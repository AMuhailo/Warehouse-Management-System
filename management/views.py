from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from employees.models import Manager
from management.models import Storage, Category, Goods
from management.tasks import replenish_goods
from management.forms import GoodsCreateForm, GoodsUpdateForm
from django.db.models import Q

# Create your views here.
class GoodsListMixin:
    model = Goods
    context_object_name = 'goods'
    
    
class GoodsDataMixin:
    model = Goods
    success_url = reverse_lazy('manage:goods_storage_url')


class GoodsURLMixin(GoodsDataMixin):
    context_object_name = 'good'
    slug_url_kwarg = 'goods_slug'
    pk_url_kwarg = 'goods_pk'
    
    
class GoodsStockMixin(GoodsURLMixin):
    def form_valid(self, form):
        cd = form.cleaned_data
        goods = form.save(commit=False)
        if cd['quantity'] > 0:
            goods.in_stock = True
        else:
            goods.in_stock = False
        goods.save()
        return super().form_valid(form)



class GoodsCreateView(GoodsStockMixin, CreateView):
    template_name = "management/goods_create.html"
    form_class = GoodsCreateForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user':self.request.user
        })
        return kwargs
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    
class GoodsStorageListView(GoodsListMixin, ListView):  
    template_name = "management/goods_storage.html"
    def get_queryset(self):
        user = self.request.user
        if user.is_manager:
            goods = Goods.objects.only('id','slug','title','quantity','price').filter(
                                                                    (Q(in_stock = True) & ~Q(quantity = 0) 
                                                                    & 
                                                                    Q(city = user.manager_user.storage)
                                                                     ))
        else:
            goods = Goods.objects.only('id','slug','title','quantity','price')
        return goods
    
    
class GoodsNotStockListView(ListView):   
    template_name = "management/goods_not_storage.html"
    queryset =  Goods.objects.only('id','title','quantity','price').filter(Q(in_stock = False) | Q(quantity = 0))
    def get_queryset(self):
        user = self.request.user
        if user.is_manager:
            goods = Goods.objects.only('id','slug','title','quantity','price').filter(
                                                                    (Q(in_stock = False) | Q(quantity = 0) 
                                                                    & 
                                                                    Q(city = user.manager_user.storage)
                                                                     ))
        else:
            goods = Goods.objects.only('id','slug','title','quantity','price').filter(Q(in_stock = False) | Q(quantity = 0))
        return goods

class GoodsUpdateView(GoodsStockMixin, UpdateView):
    form_class = GoodsUpdateForm
    template_name = 'management/goods_update.html'
    

class GoodsDeleteView(GoodsURLMixin, DeleteView):
    template_name = 'management/goods_delete.html'
    
    
class GoodsDetailView(GoodsURLMixin, DetailView):
    template_name = "management/goods_detail.html"
    
    
def scan_goods(request, goods_slug, goods_pk, action):
    good = get_object_or_404(Goods, slug = goods_slug, id = goods_pk)
    if action == 'add':
        good.quantity +=1
    elif action == 'remove' and good.quantity > 0:
        good.quantity -=1
        replenish_goods.delay(good.id)
        
    good.save()
    return JsonResponse({"massage":f"Product {good.title} updated","quantity":good.quantity})
