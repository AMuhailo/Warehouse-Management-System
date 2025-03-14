from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, ListCreateAPIView, UpdateAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from management.models import Category, Goods, Provider
from management.tasks import replenish_goods, update_goods
from api.serializers import GoodsSerializer, NoStockUpdateSerializer, CategorySerializer, ProviderSerializer
from api.permissions import IsChiefOnCreate, IsManagerUpdate
# Create your views here.


class GoodsAPIList(ListCreateAPIView):
    queryset = Goods.objects.filter((Q(in_stock = True) & ~Q(quantity = 0)) & Q(status_goods__name = 'AD')).select_related('category','city','provider')
    serializer_class = GoodsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsChiefOnCreate]
    

class NotStockAPIList(ListAPIView):
    queryset = Goods.objects.filter((Q(in_stock = False) | Q(quantity = 0)) | (Q(status_goods__name = 'MS') | Q(status_goods__name = 'SD')))
    serializer_class = GoodsSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    
class NotStockAPIUpdate(UpdateAPIView):
    queryset = Goods.objects.filter((Q(in_stock = False) | Q(quantity = 0)) | (Q(status_goods__name = 'MS') | Q(status_goods__name = 'SD')))
    serializer_class = NoStockUpdateSerializer
    permission_classes = [IsManagerUpdate, IsAuthenticated]
    
    
class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsChiefOnCreate,IsAuthenticated]
    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_object()
        goods = queryset.goods_set.all()
        goods_data = GoodsSerializer(goods, many = True).data
        category_data = CategorySerializer(queryset).data
        category_data['goods'] = goods_data
        return Response(category_data)
    
    
class ProviderViewSet(ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [IsChiefOnCreate]
    def retrieve(self, request, *args, **kwargs):
        queryset = Provider.objects.get(id = self.kwargs.get('pk'))
        goods = queryset.goods_provider.all()
        goods_data = GoodsSerializer(goods, many = True).data
        provider = ProviderSerializer(queryset).data
        provider['goods'] = goods_data
        return Response(provider)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def scan_goods_api(request, goods_slug, goods_pk):
    good = get_object_or_404(Goods, slug = goods_slug, id = goods_pk)
    action = request.data.get('action')
    if action == 'add':
            good.quantity +=1
    elif action == 'remove' and good.quantity > 0:
        good.quantity -=1
        replenish_goods.delay(good.id, request.user )
            
    good.save()
    return Response({"massage":f"Product {good.title} updated","quantity":good.quantity}, status=status.HTTP_200_OK)