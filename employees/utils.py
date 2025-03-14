from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect
from django.db.models import Count
from django.contrib.auth.mixins import LoginRequiredMixin
from employees.models import Category, Profile, Worker, Manager


class StaffURLBarrier(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_chief:
            return redirect("manage:goods_storage_url")
        return super().dispatch(request, *args, **kwargs)
    
"""  These mixins are used to optimize class workers  """
class WorkerDataMixin(LoginRequiredMixin):
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

class WorkerFilterMixin(LoginRequiredMixin):
    def get_queryset(self):
        user = self.request.user
        if user.is_chief:
            queryset = self.model.objects.filter(organisation = user.profiles, manager__isnull = False)\
                                                    .select_related('storage','category','organisation','manager','manager__user')
                
        else:
            queryset = self.model.objects.filter(organisation = user.manager_user.organisation, manager__isnull = False).select_related('storage','category','organisation','manager','manager__user')
            queryset = queryset.filter(manager__user = user)
        return queryset
    
"""  These mixins are used to optimize class manager  """
class ManagerMixin(StaffURLBarrier):
    model = Manager
    def get_queryset(self):
  
        manager = Manager.objects.filter(organisation = self.request.user.profiles)\
                                .annotate(workers = Count('worker_manager'))\
                                .select_related('user','storage')

        return manager

class ManagerDataMixin(ManagerMixin):
    context_object_name = 'manager'
    pk_url_kwarg = 'manager_pk'


