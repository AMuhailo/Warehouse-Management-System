from django import forms
from management.models import Goods

class GoodsUpdateForm(forms.ModelForm):
    class Meta:
        model = Goods
        fields = ['box']
    