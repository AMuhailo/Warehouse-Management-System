from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from management.models import Category, Goods, Provider
from management.forms import  CategoryForm
from employees.utils import StaffURLBarrier

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