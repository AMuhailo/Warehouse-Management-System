from django import forms
from management.models import Goods

class GoodsCreateForm(forms.ModelForm):
    class Meta:
        model = Goods
        exclude = ['slug','in_stock','imported','added','updated']
        
class GoodsUpdateForm(forms.ModelForm):
    class Meta:
        model = Goods
        fields = ['box','quantity']