from django.urls import include, path
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(r"category", views.CategoryViewSet, basename = 'category')
router.register(r"provider", views.ProviderViewSet, basename = 'provider')

urlpatterns = [
    path('drf-auth/',include('rest_framework.urls')),
    path('',views.GoodsAPIList.as_view()),
    path('not-stock/',views.NotStockAPIList.as_view()),
    path('not-stock/update/<pk>/',views.NotStockAPIUpdate.as_view()),
    path('management/',include(router.urls)),
    path('scan-good/<goods_slug>/<goods_pk>/', views.scan_goods_api )
]
