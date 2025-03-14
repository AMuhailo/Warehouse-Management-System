from rest_framework import serializers
from management.models import Status, Category, Goods, Provider

QUANTITY_GOODS = [(q, str(q)) for q in range(25,101,25)]

class GoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goods
        fields = ['id','category','title','quantity','price','in_stock','status_goods','city','provider']

class NoStockUpdateSerializer(serializers.Serializer):
    quantity = serializers.ChoiceField(choices = QUANTITY_GOODS)
    
    def update(self, instance, validated_data):
        status_ms = Status.objects.get(name = "MS")
        status_sd = Status.objects.get(name = "SD")
        instance.quantity =  validated_data.get('quantity')
        status_ms.goods.remove(instance.id)
        status_sd.goods.add(instance.id)
        instance.save()
        return instance
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']
        
class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['name','location','agent','email','number']
        
    