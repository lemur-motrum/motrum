from rest_framework import serializers

from apps.product.models import Cart, Lot, Price, Product, ProductProperty, Stock, ProductCart


class PriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Price
        fields = (
            "rub_price_supplier",
            "extra_price",
        )


class LotSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lot
        fields = ("name_shorts",)


class StockSerializer(serializers.ModelSerializer):

    lot = serializers.SlugRelatedField(
        slug_field="name_shorts",
        many=False,
        read_only=True,
    )

    class Meta:
        model = Stock
        fields = (
            "order_multiplicity",
            "lot",
            "lot_complect",
            "stock_supplier",
            "stock_supplier_unit",
            "stock_motrum",
            "to_order",
        )


class ProductPropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductProperty
        fields = (
            "hide",
            "name",
            "value",
        )


class ProductSerializer(serializers.ModelSerializer):
    price = PriceSerializer(read_only=True, many=False)
    stock = StockSerializer(read_only=False, many=False)
    productproperty_set = ProductPropertySerializer(read_only=False, many=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "article",
            "vendor",
            "supplier",
            "category",
            "group",
            "check_to_order",
            "price",
            "stock",
            "productproperty_set",
            "url",
        )
        
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"
        
class ProductCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCart
        fields = "__all__"        
       