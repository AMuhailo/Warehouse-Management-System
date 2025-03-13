from django.urls import path
from . import views

app_name = 'manage'

urlpatterns = [
    path('',views.GoodsStorageListView.as_view(), name = 'goods_storage_url'),
    path('storage/not-stock/', views.GoodsNotStockListView.as_view(), name = 'goods_notstock_url'),
    path('goods/created/', views.GoodsCreateView.as_view(), name = 'goods_created_url'),
    path('goods/updated/<goods_slug>/<goods_pk>/', views.GoodsUpdateView.as_view(), name = 'goods_updated_url'),
    path('goods/delete/<goods_slug>/<goods_pk>/', views.GoodsDeleteView.as_view(), name = 'goods_delete_url'),
    path('scan/<goods_slug>/<goods_pk>/<str:action>/', views.scan_goods, name = 'goods_scan_url'),  
    path('storage/add/<goods_slug>/<goods_pk>/', views.add_storage, name ='add_url'),
    path('storage/csv/', views.storage_csv, name = 'storage_csv_url'),
    path('instock-storage/csv/', views.instock_storage_csv, name = 'instock_storage_csv_url'),    
    path('import-storage-csv/', views.storage_import_csv, name = 'storage_import_csv_url'),
]

categorypatterns = [
    path('category/', views.CategoryListView.as_view() , name = 'categories_list_url'),
    path('category/create/', views.CategoryCreateView.as_view() , name = 'category_create_url'),
    path('category/<category_slug>/<category_pk>/', views.CategoryDetailView.as_view() , name = 'category_detail_url'),
    path('category/update/<category_slug>/<category_pk>/', views.CategoryUpdateView.as_view() , name = 'category_update_url'),
]

providerpatterns = [
    path('provider/', views.ProviderListView.as_view(), name = 'provider_list_url'),
    path('provider/create/', views.ProviderCreateView.as_view(), name = 'provider_create_url'),
    path('provider/<provider_name>/<provider_pk>/', views.ProviderDetailView.as_view(), name = 'provider_detail_url'),
    path('provider/update/<provider_name>/<provider_pk>/', views.ProviderUpdateView.as_view(), name = 'provider_update_url')
]

urlpatterns += categorypatterns
urlpatterns += providerpatterns