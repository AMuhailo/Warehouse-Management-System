from django import forms
from employees.models import Manager
from management.models import Goods, Provider, Status, Storage, Category
from django.utils.text import slugify

QUANTITY_GOODS = [(q, str(q)) for q in range(25,101,25)]
class GoodsCreateForm(forms.ModelForm):
    class Meta:
        model = Goods
        exclude = ['slug','in_stock','imported', 'added','updated','qr_code']
        widgets = {
            "category":forms.Select(attrs={
                "class":'form-select'
            }),
            "image":forms.FileInput(attrs={
                "class":'"form-control"',
                "id":'inputGroupFile01'
            }),
            "title":forms.TextInput(attrs={
                "class":'form-control',
            }),
            "quantity":forms.NumberInput(attrs={
                "class":'form-control',
            }),
            "price":forms.NumberInput(attrs={
                "class":'form-control',
            }),
            "city":forms.Select(attrs={
                "class":'form-select'
            }),
            "provider":forms.Select(attrs={
                "class":'form-select'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(GoodsCreateForm, self).__init__(*args, **kwargs)
        if user.is_manager:
            manager = Manager.objects.get(user = user)
            self.fields['city'].queryset = Storage.objects.filter(city = manager.storage.city, code = manager.storage.code, state = manager.storage.state)
        else:
            self.fields['city'].queryset = Storage.objects.all()
            
class GoodsUpdateForm(forms.Form):
    quantity = forms.TypedChoiceField(choices = QUANTITY_GOODS, coerce = int)
    quantity.widget.attrs.update({'class':'form-select w-50'})            

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        

class ProviderForm(forms.ModelForm):
    class Meta:
        model = Provider
        exclude = ['goods']