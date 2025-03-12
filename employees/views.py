from random import randint
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView, FormView
from employees.utils import WorkerDataMixin, WorkerFilterMixin, ManagerDataMixin, ManagerMixin
from employees.forms import ManagerCreateForm, ManagerUpdateForm, RegisterForm, WorkerCreateForm, AsignWorkerManager, CategoryUpdateForm
from employees.models import Category, Worker, Manager

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
        cd = form.cleaned_data
        category = get_object_or_404(Category, title = 'trainee')
        worker = form.save(commit = False)
        worker.manager = cd['manager']
        worker.organisation = user.manager_user.organisation
        worker.category = category
        worker.save()
        return super().form_valid(form)
    
    
class WorkerUpdateView(WorkerDataMixin, WorkerFilterMixin, UpdateView):
    form_class = WorkerCreateForm
    template_name = "employees/worker/worker_update.html"
    
    def get_success_url(self):
        return reverse('emp:worder_detail_url', args = [self.kwargs.get('worker_pk')])

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
    
class CategoryyUpdateView(WorkerFilterMixin, UpdateView):
    model = Worker
    form_class = CategoryUpdateForm
    template_name = "employees/worker/worker_category.html"
    context_object_name = 'worker'
    pk_url_kwarg = 'worker_pk'
    def get_success_url(self):
        return reverse('emp:worder_detail_url', args = [self.kwargs.get('worker_pk')])
    
""" MANAGER """
class ManagerListView(LoginRequiredMixin, ManagerMixin, ListView):
    context_object_name = 'managers'
    template_name = "employees/manager/manager_list.html"    


class ManagerCreateView(LoginRequiredMixin, ManagerMixin, CreateView):
    model = Manager
    template_name = "employees/manager/manager_create.html"
    success_url = reverse_lazy('emp:manager_list_url')
    form_class = ManagerCreateForm
    
    def form_valid(self, form, **kwargs):
        cd = form.cleaned_data
        manager = form.save(commit = False)
        manager.set_password(str(randint(1000,10000)))
        manager.is_manager = True
        manager.is_chief = False
        manager.save()
        Manager.objects.create(user = manager, organisation = self.request.user.profiles, storage = cd['storage'])
        return super().form_valid(form)
    
    
class ManagerUpdateView(LoginRequiredMixin, ManagerDataMixin, UpdateView):
    template_name = "employees/manager/manager_update.html"
    form_class = ManagerUpdateForm
    
    def get_success_url(self):
        return reverse_lazy('emp:manager_detail_url', args = [self.kwargs.get('manager_pk')])

class ManagerDetailView(LoginRequiredMixin, ManagerDataMixin, DetailView):
    template_name = "employees/manager/manager_detail.html"