from rest_framework import serializers

from apps.product.models import Lot, Price, Product, ProductProperty, Stock


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

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "article",
            "price",
            "stock",
            "productproperty_set",
        )
