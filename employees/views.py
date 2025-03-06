from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from employees.forms import RegisterForm, WorkerCreateForm
from employees.models import Category, Profile, Worker, Manager
# Create your views here

User = get_user_model()


""" MIXIN """
class WorkerDataMixin:
    model = Worker
    context_object_name = 'worker'
    success_url = reverse_lazy('emp:worker_list_url')
    pk_url_kwarg = 'worker_pk'
    
    
class RegisterCreateView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        password = form.cleaned_data['password']
        new_employeer = form.save(commit = False)
        new_employeer.set_password(password)
        new_employeer.is_chief = False
        new_employeer.is_manager = False
        new_employeer.save()
        return super().form_valid(form)
    

class WorkerListView(ListView):
    model = Worker
    context_object_name = 'workers'
    template_name = "employees/worker/worker_list.html"
    
    def get_queryset(self):
        user = self.request.user
        if user.is_chief:
            queryset = self.model.objects.filter(organisation = user.profiles, manager__isnull = False)
        else:
            queryset = self.model.objects.filter(organisation = user.manager_user.organisation, manager__isnull = False)
            queryset = queryset.filter(manager__user = user, city = user.manager_user.city)
        return queryset
    

class WorkerCreateView(WorkerDataMixin, CreateView):
    form_class = WorkerCreateForm
    template_name = 'employees/worker/worker_create.html'
    
    def form_valid(self, form):
        user = self.request.user
        category = get_object_or_404(Category, title = 'worker')
        worker = form.save(commit = False)
        
        if user.is_manager:
            worker.organisation = user.manager_user.organisation
            worker.manager = user.manager_user.user
        else:
            worker.organisation = user.profiles
            
        worker.category = category
        worker.save()
        return super().form_valid(form)
    

class WorkerDetailView(WorkerDataMixin, DetailView):
    template_name = "employees/worker/worker_detail.html"
    
class WorkerDeleteView(WorkerDataMixin, DeleteView):
    template_name = "employees/worker/worker_delete.html"

