from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from management.models import Category, Goods
from management.tasks import replenish_goods
from management.forms import GoodsCreateForm, GoodsUpdateForm
from django.db.models import Q

# Create your views here.
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
    
    def form_valid(self, form):
        return super().form_valid(form)
    
    
class GoodsStorageListView(ListView):
    model = Goods
    context_object_name = 'goods'    
    template_name = "management/goods_storage.html"
    def get_queryset(self):
        goods = Goods.objects.only('id','slug','title','quantity','price').filter(Q(in_stock = True) & ~Q(quantity = 0))
        category_slug = self.kwargs.get('category_slug')
        category_id = self.kwargs.get('category_id')
        if category_slug and category_id:
            self.category = get_object_or_404(Category, 
                                         slug = category_slug, 
                                         id = category_id)
            goods = goods.filter(category = self.category)
        else:
            self.category = None
        return goods
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["category"] = self.category
        return context
    
    
class GoodsNotStockListView(ListView):
    model = Goods
    context_object_name = 'goods'    
    template_name = "management/goods_not_storage.html"
    queryset =  Goods.objects.only('id','title','quantity','price').filter(Q(in_stock = False) | Q(quantity = 0))


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
