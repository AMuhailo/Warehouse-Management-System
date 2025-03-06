from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView
from employees.forms import RegisterForm, WorkerCreateForm
from employees.models import Category, Profile, Worker, Manager
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
    

class WorkerListView(ListView):
    model = Worker
    context_object_name = 'workers'
    template_name = "employees/worker/worker_list.html"
    
    def get_queryset(self):
        user = self.request.user
        return self.model.objects.filter(organisation = user.profiles)
    

class WorkerCreateView(CreateView):
    model = Worker
    context_object_name = 'worker'
    form_class = WorkerCreateForm
    template_name = 'employees/worker/worker_create.html'
    success_url = reverse_lazy('emp:worker_list_url')
    
    def form_valid(self, form):
        category = get_object_or_404(Category, title = 'worker')
        worker = form.save(commit = False)
        worker.organisation = self.request.user.profiles
        worker.category = category
        worker.save()
        return super().form_valid(form)
    

class WorkerDetailView(DetailView):
    model = Worker
    context_object_name = 'worker'
    pk_url_kwarg = 'worker_pk'
    template_name = "employees/worker/worker_detail.html"
    

class WorkerDeleteView(DeleteView):
    model = Worker
    context_object_name = 'worker'
    pk_url_kwarg = 'worker_pk'
    template_name = "employees/worker/worker_delete.html"
    success_url = reverse_lazy('emp:worker_list_url')