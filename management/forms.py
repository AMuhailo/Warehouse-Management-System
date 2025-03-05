from django import forms
from management.models import Goods

class GoodsCreateForm(forms.ModelForm):
    class Meta:
        model = Goods
        exclude = ['slug','in_stock','imported', 'provider', 'added','updated']
        
class GoodsUpdateForm(forms.ModelForm):
    class Meta:
        model = Goods
        fields = ['quantity']