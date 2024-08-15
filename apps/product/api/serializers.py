from rest_framework import serializers

from apps.product.models import Price, Product, ProductProperty, Stock



        
        
class PriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Price
        fields = "__all__"
        
class StockSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stock
        fields = "__all__"
        
        
class ProductPropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductProperty
        fields = "__all__"  
        
        
class ProductSerializer(serializers.ModelSerializer):
    # price_set = PriceSerializer(read_only=False, many=True)
    # stock_set = StockSerializer(read_only=False, many=True)
    # productproperty_set = ProductPropertySerializer(read_only=False, many=True)
    class Meta:
        model = Product
        fields = ("name",)          
        
class ProductTestSerializer(serializers.ModelSerializer):
    price = PriceSerializer(read_only=True, many=False)
    stock = StockSerializer(read_only=False, many=False)
    productproperty_set = ProductPropertySerializer(read_only=False, many=True)   
    class Meta:
        model = Product
        fields = "__all__"                             
        
