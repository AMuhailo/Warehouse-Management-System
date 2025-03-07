from random import randint
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView, FormView
from employees.forms import RegisterForm, WorkerCreateForm, AsignWorkerManager
from employees.models import Category, Profile, Worker, Manager
# Create your views here

User = get_user_model()


""" MIXIN """
    
class WorkerDataMixin:
    model = Worker
    context_object_name = 'worker'
    success_url = reverse_lazy('emp:worker_list_url')
    pk_url_kwarg = 'worker_pk'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request':self.request
        })
        return kwargs

class WorkerFilterMixin:
    def get_queryset(self):
        user = self.request.user
        if user.is_chief:
            queryset = self.model.objects.filter(organisation = user.profiles, manager__isnull = False)
        else:
            queryset = self.model.objects.filter(organisation = user.manager_user.organisation, manager__isnull = False)
            queryset = queryset.filter(manager__user = user)
        return queryset
    


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
    
    
""" WORKER """
class WorkerListView(WorkerFilterMixin,  ListView):
    model = Worker
    template_name = "employees/worker/worker_list.html"
    context_object_name = 'workers'
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context["unassigned_workes"] = Worker.objects.filter(organisation = user.profiles , manager__isnull = True)
        return context


class WorkerCreateView(WorkerDataMixin, WorkerFilterMixin, CreateView):
    form_class = WorkerCreateForm
    template_name = 'employees/worker/worker_create.html'
    
       
    def form_valid(self, form):
        user = self.request.user
        category = get_object_or_404(Category, title = 'worker')
        worker = form.save(commit = False)
        worker.manager = form.cleaned_data['manager']
        worker.organisation = user.profiles
        worker.category = category
        worker.save()
        return super().form_valid(form)
    
class WorkerUpdateView(WorkerDataMixin, WorkerFilterMixin, UpdateView):
    form_class = WorkerCreateForm
    template_name = "employees/worker/worker_update.html"
    
    
class WorkerDetailView(WorkerDataMixin, WorkerFilterMixin, DetailView):
    template_name = "employees/worker/worker_detail.html"
    
    
class WorkerDeleteView(WorkerDataMixin, WorkerFilterMixin, DeleteView):
    template_name = "employees/worker/worker_delete.html"



class WorkerAsignFormView(FormView):
    template_name = "employees/worker/worker_asign.html"
    form_class = AsignWorkerManager
    
    def get_form_kwargs(self, **kwargs):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request':self.request
            })
        return kwargs
    
    def get_success_url(self):
        return reverse("emp:worker_list_url")
    
    def form_valid(self, form):
        manager = form.cleaned_data['manager']
        worker = get_object_or_404(Worker, id = self.kwargs.get('worker_pk'))
        worker.manager = manager
        worker.save()
        return super(WorkerAsignFormView, self).form_valid(form)
    