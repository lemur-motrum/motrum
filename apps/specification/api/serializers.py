from rest_framework import serializers

from apps.client.models import Order
from apps.product.api.serializers import (
    ProductSerializer,
    ProductSpesifSerializer,
    StockSerializer,
)
from apps.product.models import CategoryProduct, Product, ProductCart, Stock
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
        representation = super(SpecificationSerializer, self).to_representation(
            instance
        )
        if instance.date_stop:
            representation["date_stop"] = instance.date_stop.strftime("%d.%m.%Y")
        if instance.total_amount:
            representation["total_amount"] = (
                "{0:,}".format(instance.total_amount).replace(",", " ").replace(".", ",")
            )
        if instance.date:
            representation["date"] = instance.date.strftime("%d.%m.%Y")
        if instance.date_update:
            representation["date_update"] = instance.date_update.strftime("%d.%m.%Y")
        return representation


class ProductSpecificationSerializer(serializers.ModelSerializer):
    product_okt_name = serializers.SerializerMethodField()
    product_okt_article = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductSpecification
        fields = (
            "id",
            "product_okt_name",
            "product_okt_article",
            "product_new",
            "product_new_article",
            "quantity",
            "date_delivery",
            "text_delivery",
            "stock",
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

    def get_stock(self, obj):
        if obj.product:
            stock_item = Stock.objects.get(prod_id=obj.product_id)
            serializer = StockSerializer(stock_item, many=False)
            return serializer.data
        else:
            return None


class ProductSpecificationSaveSerializer(serializers.ModelSerializer):
    product_okt_name = serializers.SerializerMethodField()
    product_okt_article = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductSpecification
        fields = "__all__"


class ProductSpecificationToAddBillSerializer(serializers.ModelSerializer):
    product_okt_name = serializers.SerializerMethodField()
    product_okt_article = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    text_delivery_bill = serializers.SerializerMethodField()

    class Meta:
        model = ProductSpecification
        fields = (
            "id",
            "product_okt_name",
            "product_okt_article",
            "product_new",
            "product_new_article",
            "quantity",
            "date_delivery",
            "text_delivery",
            "stock",
            "text_delivery_bill",
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

    def get_stock(self, obj):
        if obj.product:
            stock_item = Stock.objects.get(prod_id=obj.product_id)
            serializer = StockSerializer(stock_item, many=False)
            return serializer.data
        else:
            return None

    def get_text_delivery_bill(self, obj):
        order = Order.objects.get(specification_id=obj.specification.id)
        product_cart = ProductCart.objects.filter(cart=order.cart)
        if obj.product:
            product_cart.filter(product=obj.product)
        else:
            product_cart.filter(product_new=obj.product_new)


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
            "number",
            "name_prefix",
        )

    def to_representation(self, instance):
        representation = super(
            ListsProductSpecificationSerializer, self
        ).to_representation(instance)
        representation["date"] = instance.date.strftime("%d.%m.%Y")
        if instance.date_stop:
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
            "number",
        )

    def to_representation(self, instance):
        representation = super(ListsSpecificationSerializer, self).to_representation(
            instance
        )
        representation["date"] = instance.date.strftime("%d.%m.%Y")
        if instance.date_stop:
            representation["date_stop"] = instance.date_stop.strftime("%d.%m.%Y")
        return representation


class ProductSpecification1cSerializer(serializers.ModelSerializer):
    # product_okt_name = serializers.SerializerMethodField()
    # product_okt_article = serializers.SerializerMethodField()
    # stock = serializers.SerializerMethodField()
    # article = serializers.CharField(source="product.article")
    article_motrum = serializers.SerializerMethodField()
    class Meta:
        model = ProductSpecification
        fields = (
            
            "article_motrum",
            "date_delivery",
            "reserve",
            "client_shipment",
            "date_shipment",)

    def get_article_motrum(self, obj):
        print("obj",obj)
        # if obj.product:
        #     article_supplier = Product.objects.get(id=obj.product_id).article_supplier
        #     # product_okt_name

        #     return article_supplier
        # else:
        #     return None