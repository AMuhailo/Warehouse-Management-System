from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from management.models import Category, Goods
from management.forms import GoodsUpdateForm
from django.db.models import Q

# Create your views here.
class GoodsCreateView(CreateView):
    model = Goods
    template_name = "management/goodscreate.html"
    success_url = reverse_lazy('manage:')
    
    
class GoodsStorageListView(ListView):
    model = Goods
    context_object_name = 'goods'    
    template_name = "management/goods_storage.html"
    def get_queryset(self):
        goods = Goods.objects.only('id','title','box','price').filter(Q(in_stock = True) & ~Q(box = 0))
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
    queryset =  Goods.objects.only('id','title','box','price').filter(Q(in_stock = False) | Q(box = 0))


class GoodsUpdateView(UpdateView):
    model = Goods
    form_class = GoodsUpdateForm
    context_object_name = 'good'
    slug_url_kwarg = 'goods_slug'
    pk_url_kwarg = 'goods_pk'
    success_url = reverse_lazy('manage:goods_storage_url')
    template_name = 'management/goods_update.html'

    def form_valid(self, form):
        cd = form.cleaned_data['box']
        goods = form.save(commit=False)
        if cd > 0:
            goods.in_stock = True
        else:
            goods.in_stock = False
        goods.save()
        return super().form_valid(form)
    