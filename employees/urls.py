from django.urls import path
from . import views

app_name = 'emp'

urlpatterns = [
    path('worker/',views.WorkerListView.as_view(), name = 'worker_list_url'),
    path('worker/create/', views.WorkerCreateView.as_view(), name = 'worder_create_url')
]
