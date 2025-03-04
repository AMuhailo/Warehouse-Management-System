from django import forms
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(min_length = 8, widget = forms.PasswordInput)
    password2 = forms.CharField(min_length = 8, widget = forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password','password2']
        
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password2'] != cd['password']:
            raise forms.ValidationError('Password don`t similar.Please repeat!')
        return cd['password']
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','last_name','email']
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image','birthday']
        