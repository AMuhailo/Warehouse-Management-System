from django import forms
from employees.models import Manager
from management.models import Goods, Provider, Storage, Category
from django.utils.text import slugify
class GoodsCreateForm(forms.ModelForm):
    class Meta:
        model = Goods
        exclude = ['slug','in_stock','imported', 'added','updated','qr_code']
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(GoodsCreateForm, self).__init__(*args, **kwargs)
        if user.is_manager:
            manager = Manager.objects.get(user = user)
            self.fields['city'].queryset = Storage.objects.filter(city = manager.storage.city, code = manager.storage.code)
        else:
            self.fields['city'].queryset = Storage.objects.all()
            
class GoodsUpdateForm(forms.ModelForm):
    class Meta:
        model = Goods
        fields = ['quantity']
        
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        

class ProviderForm(forms.ModelForm):
    class Meta:
        model = Provider
        exclude = ['goods']