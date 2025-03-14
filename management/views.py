import csv
from datetime import datetime
from django.http import JsonResponse , HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.db.models import Count
from django.db.models import Q
from management.utils import GoodsDataMixin, CategoryMixin, CategoryDataMixin, CategoryFormMixin, ProviderMixin, ProviderDataMixin
from management.models import Status, Category, Goods, Provider, Storage
from management.tasks import replenish_goods, update_goods
from management.forms import GoodsCreateForm, GoodsUpdateForm, CategoryForm, ProviderForm


# Create your views here.
class GoodsCreateView(LoginRequiredMixin, CreateView):
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
    
    
class GoodsStorageListView(LoginRequiredMixin, ListView):  
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
    
    
class GoodsNotStockListView(LoginRequiredMixin, ListView):   
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
        
class GoodsDeleteView(LoginRequiredMixin, DeleteView):
    model = Goods
    template_name = 'management/goods/goods_delete.html'
    context_object_name = 'good'
    slug_url_kwarg = 'goods_slug'
    pk_url_kwarg = 'goods_pk'
    
    

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
    
    def get_queryset(self):
        categories = Category.objects.all().annotate(category = Count('goods'))
        return categories
    
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
    def get_queryset(self):       
        provider = Provider.objects.only('id','name','agent','email','number')
        return provider

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
    
    
def storage_csv(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = "attachment; filename=storage_goods.csv"
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Category', 'Title', 'Quantity', 'Price', 'In Stock', 'City', 'Provider', 'Imported'])
    goods = Goods.objects.all().values_list('id','category__name','title','quantity','price','in_stock','city__city','provider__name','imported')
    for good in goods:
        writer.writerow(good)
    return response

def instock_storage_csv(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = f"attachment; filename=not-torage-{datetime.now()}.csv"    
    writer = csv.writer(response)
    user = request.user
    writer.writerow(['ID', 'Category', 'Title', 'Quantity', 'Price', 'In Stock', 'Status', 'City', 'Provider', 'Imported'])
    if user.is_manager:
        goods = Goods.objects\
                        .filter(
                            (Q(in_stock = False) | Q(quantity = 0)) 
                            & 
                            (Q(city = user.manager_user.storage) | (Q(status_goods__name = 'MS') | Q(status_goods__name = 'SD')))
                            ).select_related('category','city','provider').prefetch_related("status_goods").values_list('id','category__name','title','quantity','price','in_stock','status_goods__name','city__city','provider__name','imported')
    else:
        goods = Goods.objects\
                        .filter(
                            (Q(in_stock = False) | Q(quantity = 0)) | (Q(status_goods__name = 'MS') | Q(status_goods__name = 'SD'))
                            ).select_related('category','city','provider').prefetch_related("status_goods").values_list('id','category__name','title','quantity','price','in_stock','status_goods__name','city__city','provider__name','imported')
    for good in goods:
        writer.writerow(good)
    return response


def storage_import_csv(request):
    if request.method == "POST" and request.FILES.get('file'):
        csv_f = request.FILES['file']
        file = csv_f.read().decode('utf-8').splitlines()
        reader = csv.reader(file)
        next(reader)
        
        for row in reader:
            category = get_object_or_404(Category, id=row[1])
            city = get_object_or_404(Storage, id=row[6])
            provider = get_object_or_404(Provider, id=row[7])
            
            Goods.objects.create(category = category,
                                 title = row[2],
                                 slug = row[2].lower().replace(" ", "-"),
                                 quantity = row[3],
                                 price = row[4],
                                 in_stock = row[5],
                                 city = city,
                                 provider = provider,
                                 imported = row[8])
        return redirect('manage:goods_storage_url')
    return render(request,'management/goods/import_csv.html')
            