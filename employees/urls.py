from django.urls import path
from . import views

app_name = 'emp'

urlpatterns = [
    path('worker/',views.WorkerListView.as_view(), name = 'worker_list_url'),
    path('worker/create/', views.WorkerCreateView.as_view(), name = 'worder_create_url'),
    path('worker/<worker_pk>/', views.WorkerDetailView.as_view(), name = 'worder_detail_url'),
    path('worker/delete/<worker_pk>/', views.WorkerDeleteView.as_view(), name = 'worker_delete_url')
]

managerpatterns = [
    
]