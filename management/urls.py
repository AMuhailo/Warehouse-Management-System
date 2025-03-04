from django.urls import path
from . import views

app_name = 'manage'

urlpatterns = [
    path('',views.GoodsStorageListView.as_view(), name = 'goods_storage_url'),
    path('category/<category_slug>/<category_id>/',views.GoodsStorageListView.as_view(), name = 'goods_category_url'),
    path('storage/not-stock/', views.GoodsNotStockListView.as_view(), name = 'goods_notstock_url'),
    path('goods/created/', views.GoodsCreateView.as_view(), name = 'goods_created_url'),
    path('goods/updated/<goods_slug>/<goods_pk>/', views.GoodsUpdateView.as_view(), name = 'goods_updated_url'),
]