from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from employees.forms import RegisterForm, UserForm, ProfileForm
from employees.models import Profile
# Create your views here

User = get_user_model()

class RegisterCreateView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        password = form.cleaned_data['password']
        new_employeer = form.save(commit = False)
        new_employeer.set_password(password)
        new_employeer.save()
        return super().form_valid(form)


class ProfileUpdateView(UpdateView):
    model = Profile
    form_class =  UserForm
    template_name = "registration/profileupdate.html"
    success_url = reverse_lazy('login')
    
    def get_object(self, queryset = ...):
        return User.objects.get(username = self.kwargs.get('username'))
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_form"] = self.form_class(instance = self.get_object())
        context["profile_form"] = ProfileForm(data = self.request.GET , instance = self.get_object().profiles ,files = self.request.FILES)
        return context
    
    
