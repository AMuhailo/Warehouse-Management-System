import csv
from django.http import HttpResponse
from random import randint
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, ListView, DetailView, DeleteView, FormView
from employees.utils import WorkerDataMixin, WorkerFilterMixin, ManagerDataMixin, ManagerMixin
from employees.forms import ManagerCreateForm, ManagerUpdateForm, RegisterForm, WorkerCreateForm, AsignWorkerManager, CategoryUpdateForm
from employees.models import Category, Worker, Manager
from employees.tasks import added_to_manager
from management.models import Storage
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
        if user.is_manager:
            worker.organisation = user.manager_user.organisation
        else:
            worker.organisation = user.profiles
        worker.category = category
        worker.save()
        return super().form_valid(form)
    
    
class WorkerUpdateView(WorkerDataMixin, WorkerFilterMixin, UpdateView):
    form_class = WorkerCreateForm
    template_name = "employees/worker/worker_update.html"
    
    def get_success_url(self):
        return reverse('emp:worder_detail_url', args = [self.kwargs.get('worker_pk')])
    
    def get_object(self, queryset = ...):
        return get_object_or_404(Worker, pk = self.kwargs.get('worker_pk'))
class WorkerDetailView(WorkerDataMixin, WorkerFilterMixin, DetailView):
    template_name = "employees/worker/worker_detail.html"
    
    def get_object(self, queryset = ...):
        return get_object_or_404(Worker, pk = self.kwargs.get('worker_pk'))
   
class WorkerDeleteView(WorkerDataMixin, WorkerFilterMixin, DeleteView):
    template_name = "employees/worker/worker_delete.html"
    
    def get_object(self, queryset = ...):
        return get_object_or_404(Worker, pk = self.kwargs.get('worker_pk'))

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
        added_to_manager.delay(manager)
        return super().form_valid(form)
    
    
class ManagerUpdateView(LoginRequiredMixin, ManagerDataMixin, UpdateView):
    template_name = "employees/manager/manager_update.html"
    form_class = ManagerUpdateForm
    
    def get_success_url(self):
        return reverse_lazy('emp:manager_detail_url', args = [self.kwargs.get('manager_pk')])

    def get_object(self, queryset = ...):
        return get_object_or_404(Manager, pk = self.kwargs.get('manager_pk'))
    
class ManagerDetailView(LoginRequiredMixin, ManagerDataMixin, DetailView):
    template_name = "employees/manager/manager_detail.html"
    
    def get_object(self, queryset = ...):
        return get_object_or_404(Manager, pk = self.kwargs.get('manager_pk'))
    
def worker_csv(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = "attachment; filename=worker_goods.csv"
    
    writer = csv.writer(response)
    writer.writerow(['ID',"First Name", "Last Name", "Age", "Phone", "City", "Street", "State", "Category", "Manager"])
    workers = Worker.objects.all().values_list('id','first_name', 'last_name', 'age', 'phone', 'storage__city', 'storage__street', 'storage__state', 'category__title', 'manager__user__username')
    for worker in workers:
        writer.writerow(worker)
    return response
    
    
def worker_import_csv(request):
    if request.method == "POST" and request.FILES.get("file"):
        csv_f = request.FILES['file']
        file = csv_f.read().decode('utf-8').splitlines()
        reader = csv.reader(file)
        next(reader)
    
        for row in reader:
            storage = Storage.objects.create(city = row[5],
                                street = row[6],
                                state = row[7])
            storage.save()
            category = Category.objects.get(title = row[8])
            manager = Manager.objects.get(user__username = row[9])
            Worker.objects.create(first_name = row[1],
                                last_name = row[2],
                                age = row[3],
                                phone = row[4],
                                storage = storage,
                                category = category,
                                organisation = request.user.profiles,
                                manager = manager)
        return redirect('emp:worker_import_csv_url')
    return render(request,'employees/worker/import_csv.html')