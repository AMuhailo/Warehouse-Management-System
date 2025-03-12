from django import forms
from django.contrib.auth import get_user_model
from employees.models import Manager, Profile, Worker
from management.models import Storage

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
    
        
class WorkerCreateForm(forms.ModelForm):
    class Meta:
        model = Worker
        exclude = ['organisation','category']
    
    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        super(WorkerCreateForm, self).__init__(*args, **kwargs)
        if request.user.is_manager:
            manager = Manager.objects.filter(user = request.user)
            self.fields['manager'].queryset = manager
            self.fields['storage'].queryset = Storage.objects.filter(city = request.user.manager_user.storage.city)
        else:
            manager = Manager.objects.filter(organisation = request.user.profiles)
            self.fields['manager'].queryset = manager
            
            
class AsignWorkerManager(forms.Form):
    manager = forms.ModelChoiceField(queryset = Manager.objects.none())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request')
        manager = Manager.objects.filter(organisation = request.user.profiles)
        super(AsignWorkerManager, self).__init__(*args, **kwargs)
        self.fields['manager'].queryset = manager
        
        
        
class ManagerCreateForm(forms.ModelForm):
    storage = forms.ModelChoiceField(queryset = Storage.objects.all())
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','storage']
        
        
class ManagerUpdateForm(forms.ModelForm):
    class Meta:
        model = Manager
        exclude = ['organisation']
        
        
class CategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ['category']
