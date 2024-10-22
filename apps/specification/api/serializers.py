from rest_framework import serializers

from apps.product.api.serializers import (
    ProductSerializer,
    ProductSpesifSerializer,
    StockSerializer,
)
from apps.product.models import Product, Stock
from apps.specification.models import ProductSpecification, Specification


class SpecificationSerializer(serializers.ModelSerializer):
    # date = serializers.DateField(format="%Y-%m-%d")
    # date_update = serializers.DateField(format="%Y-%m-%d")
    # date_stop = serializers.DateField(format="%Y-%m-%d")
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    url_history = serializers.CharField(source="get_history_url", read_only=True)
    admin_creator_name = serializers.CharField(source="admin_creator")
    class Meta:
        model = Specification
        fields = "__all__"
        
    def to_representation(self, instance):
        representation = super(
            SpecificationSerializer, self
        ).to_representation(instance)
        
        representation["date_stop"] = instance.date_stop.strftime("%d.%m.%Y")
        representation["total_amount"] = '{0:,}'.format(instance.total_amount).replace(',', ' ')
        return representation      


class ProductSpecificationSerializer(serializers.ModelSerializer):
    product_okt_name = serializers.SerializerMethodField()
    product_okt_article = serializers.SerializerMethodField()
    class Meta:
        model = ProductSpecification
        fields = (
            "id",
            "product_okt_name",
            'product_okt_article',
            "product_new",
            "product_new_article",
            "quantity",
        )
    
    def get_product_okt_name(self, obj):
        if obj.product:
            product_okt_name = Product.objects.get(id=obj.product_id).name
            # product_okt_name 

            return product_okt_name
        else:
            return None  
         
    def get_product_okt_article(self, obj):
        if obj.product:
            article_supplier = Product.objects.get(id=obj.product_id).article_supplier
            # product_okt_name 

            return article_supplier
        else:
            return None      


class ListProductSpecificationSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(source="product.name")
    product_id = serializers.CharField(source="product.id")
    lot = serializers.SerializerMethodField()

    class Meta:
        model = ProductSpecification
        fields = (
            "id",
            "product_name",
            "product_id",
            "quantity",
            "lot",
        )

    def get_lot(self, obj):
        stock_item = Stock.objects.get(prod_id=obj.product_id)
        serializer = StockSerializer(stock_item, many=False)

        return serializer.data


class ListsProductSpecificationSerializer(serializers.ModelSerializer):
    productspecification_set = ListProductSpecificationSerializer(
        read_only=False, many=True
    )

    class Meta:
        model = Specification
        fields = (
            "id",
            "file",
            "date",
            "date_stop",
            "total_amount",
            "productspecification_set",
        )

    def to_representation(self, instance):
        representation = super(
            ListsProductSpecificationSerializer, self
        ).to_representation(instance)
        representation["date"] = instance.date.strftime("%d.%m.%Y")
        representation["date_stop"] = instance.date_stop.strftime("%d.%m.%Y")
        return representation


class ListsSpecificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Specification
        fields = (
            "id",
            "file",
            "date",
            "date_stop",
            "total_amount",
        )

    def to_representation(self, instance):
        representation = super(
            ListsSpecificationSerializer, self
        ).to_representation(instance)
        representation["date"] = instance.date.strftime("%d.%m.%Y")
        representation["date_stop"] = instance.date_stop.strftime("%d.%m.%Y")
        return representation
