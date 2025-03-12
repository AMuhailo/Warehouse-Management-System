from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from employees.models import Manager
from django.db.models import Count
from employees.utils import StaffURLBarrier
from management.models import Status, Storage, Category, Goods, Provider
from management.tasks import replenish_goods, update_goods
from management.forms import GoodsCreateForm, GoodsUpdateForm, CategoryForm, ProviderForm
from django.db.models import Q

# Create your views here.

class GoodsDataMixin(LoginRequiredMixin):
    model = Goods
    success_url = reverse_lazy('manage:goods_storage_url')


class CategoryMixin(LoginRequiredMixin):
    model = Category


class CategoryDataMixin(CategoryMixin):
    context_object_name = 'category'
    slug_url_kwarg = 'category_slug'
    pk_url_kwarg = 'category_pk'
    
class CategoryFormMixin(CategoryDataMixin):    
    template_name = 'management/category/category_create.html'
    form_class = CategoryForm
    success_url = reverse_lazy('manage:categories_list_url')
    
    
class ProviderMixin(StaffURLBarrier):
    model = Provider

class ProviderDataMixin(ProviderMixin):
    slug_url_kwarg = 'provider_name'
    pk_url_kwarg = 'provider_pk'
    context_object_name = 'provider'


class GoodsCreateView(CreateView):
    model = Goods
    template_name = "management/goods/goods_create.html"
    form_class = GoodsCreateForm
    success_url = reverse_lazy("manage:goods_storage_url")
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'user':self.request.user
        })
        return kwargs
    
    def form_valid(self, form):
        cd = form.cleaned_data
        goods = form.save(commit=False)
        if cd['quantity'] > 0:
            goods.in_stock = True
        else:
            goods.in_stock = False
        goods.save()
        status = Status.objects.get(name = "AD")
        status.goods.add(goods.id)
        return super().form_valid(form)
    
    
class GoodsStorageListView(ListView):  
    model = Goods
    context_object_name = 'goods'
    template_name = "management/goods/goods_storage.html"
    def get_queryset(self):
        user = self.request.user
        if user.is_manager:
            goods = Goods.objects\
                                .filter(
                                    (Q(in_stock = True) & ~Q(quantity = 0)) & (Q(city = user.manager_user.storage) & Q(status_goods__name = 'AD'))
                                    ).select_related('category','provider','city')
        else:
            goods = Goods.objects\
                                .filter(
                                    (Q(in_stock = True) & ~Q(quantity = 0)) & Q(status_goods__name = 'AD')
                                    ).select_related('category','city','provider')
        return goods
    
    
class GoodsNotStockListView(ListView):   
    model = Goods
    template_name = "management/goods/goods_not_storage.html"
    context_object_name = 'goods'
    def get_queryset(self):
        user = self.request.user
        if user.is_manager:
            goods = Goods.objects\
                                .filter(
                                    (Q(in_stock = False) | Q(quantity = 0)) 
                                    & 
                                    (Q(city = user.manager_user.storage) | (Q(status_goods__name = 'MS') | Q(status_goods__name = 'SD')))
                                    ).select_related('category','city','provider').prefetch_related("status_goods")
        else:
            goods = Goods.objects\
                                .filter(
                                    (Q(in_stock = False) | Q(quantity = 0)) | (Q(status_goods__name = 'MS') | Q(status_goods__name = 'SD'))
                                    ).select_related('category','city','provider').prefetch_related("status_goods")
        return goods
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update_form"] = GoodsUpdateForm()
        return context

class GoodsUpdateView(GoodsDataMixin, UpdateView):
    model = Goods
    context_object_name = 'good'
    slug_url_kwarg = 'goods_slug'
    pk_url_kwarg = 'goods_pk'
    form_class = GoodsUpdateForm
    template_name = 'management/goods/goods_update.html'
    success_url = reverse_lazy('manage:goods_notstock_url')
    def get_form(self, form_class = ...):
        form_class = self.get_form_class()
        return form_class(data = self.request.POST or None)
    
    def form_valid(self, form):
        status_ms = Status.objects.get(name = "MS")
        status_sd = Status.objects.get(name = "SD")
        cd = form.cleaned_data['quantity']
        goods = get_object_or_404(Goods, 
                                  slug = self.kwargs.get('goods_slug'), 
                                  id  = self.kwargs.get('goods_pk'))
        goods.increase(quantity = cd, status = status_ms)
        status_sd.goods.add(goods.pk)
        update_goods.delay(goods.pk, cd)
        goods.save()
        return redirect('manage:goods_notstock_url')
        
class GoodsDeleteView(DeleteView):
    model = Goods
    template_name = 'management/goods/goods_delete.html'
    context_object_name = 'good'
    slug_url_kwarg = 'goods_slug'
    pk_url_kwarg = 'goods_pk'
    
    
def scan_goods(request, goods_slug, goods_pk, action):
    good = get_object_or_404(Goods, slug = goods_slug, id = goods_pk)
    if action == 'add':
        good.quantity +=1
    elif action == 'remove' and good.quantity > 0:
        good.quantity -=1
        replenish_goods.delay(good.id, request.user )
        
    good.save()
    return JsonResponse({"massage":f"Product {good.title} updated","quantity":good.quantity})

def add_storage(request, goods_slug, goods_pk):
    good = get_object_or_404(Goods, slug = goods_slug, id = goods_pk)
    statuses = good.status_goods.all()
    if statuses.filter(name = "SD").exists:
        status_sd = Status.objects.get(name = 'SD')
        status_sd.goods.remove(good.pk)
        status_ad = Status.objects.get(name = "AD")
        status_ad.goods.add(good.pk)
        good.in_stock = True
        good.save()
    return redirect('manage:goods_storage_url')

class CategoryListView(CategoryMixin, ListView):
    template_name = 'management/category/category_list.html'
    context_object_name = 'categories'
    queryset = Category.objects.all().annotate(category = Count('goods'))
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CategoryForm 
        return context
    
    
class CategoryDetailView(CategoryDataMixin, DetailView):
    template_name = 'management/category/category_detail.html'
    def get_object(self, queryset = ...):
        category = Category.objects.prefetch_related('goods_set__provider','goods_set__city')
        return get_object_or_404(category, slug = self.kwargs.get('category_slug'), id = self.kwargs.get('category_pk'))
    
class CategoryCreateView(CategoryFormMixin, CreateView): pass
    
    
class CategoryUpdateView(CategoryFormMixin, UpdateView): pass


class ProviderListView(ProviderMixin, ListView):
    context_object_name = 'providers'
    template_name = 'management/provider/provider_list.html'
    queryset = Provider.objects.only('id','name','agent','email','number')


class ProviderDetailView(ProviderDataMixin, DetailView):
    template_name = 'management/provider/provider_detail.html'
    
    
    
class ProviderCreateView(ProviderMixin, CreateView):
    template_name = 'management/provider/provider_create.html'
    success_url = reverse_lazy('manage:provider_list_url')
    form_class = ProviderForm

    
class ProviderUpdateView(ProviderDataMixin, UpdateView):
    template_name = 'management/provider/provider_update.html'
    form_class = ProviderForm
    
    def get_success_url(self):
        return reverse('manage:provider_detail_url', args=[self.kwargs.get('provider_name'), self.kwargs.get('provider_pk')])