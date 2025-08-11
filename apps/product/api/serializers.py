from apps.supplier.models import Vendor
from rest_framework import serializers
from sorl.thumbnail import get_thumbnail


from apps.client.models import Client
from apps.product.models import (
    Cart,
    Lot,
    Price,
    Product,
    ProductImage,
    ProductProperty,
    Stock,
    ProductCart,
)


class PriceSerializer(serializers.ModelSerializer):
    current_user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Price
        fields = (
            "rub_price_supplier",
            "extra_price",
            "current_user",
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
            "stock_motrum_reserve",
            "to_order",
            "data_update",
            "transit_count",
        )


class ProductPropertySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductProperty
        fields = (
            "id",
            "hide",
            "name",
            "value",
        )


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = (
            "id",
            "hide",
            "photo",
        )



class ProductSpesifSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
        )


class ProductSearchSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    class Meta:
        model = Product
        fields = (
            "id",
            "article_supplier",
            "name",
            "url",
            "description",
        )
    
class VendorSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"
    


class ProductSerializer(serializers.ModelSerializer):
    price = PriceSerializer(read_only=True, many=False)
    stock = StockSerializer(read_only=False, many=False)
    productproperty_set = ProductPropertySerializer(read_only=False, many=True)
    productimage_set = ProductImageSerializer(read_only=False, many=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    supplier_slug = serializers.ReadOnlyField(source="supplier.slug")
    # product_name = serializers.SerializerMethodField()
    # image_small = serializers.SerializerMethodField()
    # max_price = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "article",
            "article_supplier",
            "vendor",
            "supplier",
            "supplier_slug",
            "category",
            "group",
            "check_to_order",
            "price",
            "stock",
            "productproperty_set",
            "productimage_set",
            "url",
            # "product_name"
            # "image_small",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data["price"] and data["price"]["rub_price_supplier"]:
            if (
                self.context
                and self.context["request"]
                and self.context["request"].user
            ):
                if self.context["request"].user.is_staff == False:
                    try:
                        client = Client.objects.get(id=self.context["request"].user.id)
                        if client.percent:
                            discount = client.percent
                        else:
                            discount = 100
                    except Client.DoesNotExist:
                        client = None
                        discount = 100
                    price = data["price"]["rub_price_supplier"]
                    if discount == 100:
                        price_discount = price
                    else:
                        price_discount = price - (price / 100 * float(discount))
                    data["price"]["rub_price_supplier"] = round(price_discount, 2)
        if len(data["productimage_set"]) > 0:
            # crop='center', quality=99
            data["productimage_set"][0]["photo"]  = get_thumbnail(data["productimage_set"][0]["photo"], '200x200',format="PNG",quality=50 ).url
      
        if data["supplier_slug"] == "iek":
            data["name"] = f"{data["article_supplier"]} {data["name"]}"
        return data

    # def get_product_name(self, obj):

    #     if obj.vendor.slug == "oni":
    #         return f"{obj.article_supplier} {obj.name}"
    #     else:
    #         return f"{obj.name}"
    
    # def get_image_small(self, obj):
    #     image_small = get_thumbnail(data["productimage_set"][0], '200x200', crop='center', quality=99).url
    #     return image_small

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"


class ProductCartSerializer(serializers.ModelSerializer):
    product_id_name = serializers.SerializerMethodField()

    class Meta:
        model = ProductCart
        fields = "__all__"

    def get_product_id_name(self, obj):

        if obj.product:
            return f"{obj.product.article_supplier} {obj.product.name}"
        else:
            return None


class CartOktAllSerializer(serializers.ModelSerializer):
    productcart_set = ProductCartSerializer(read_only=True, many=True)
    admin_creator_name = serializers.CharField(source="cart_admin")

    class Meta:
        model = Cart
        fields = (
            "id",
            "cart_admin",
            "admin_creator_name",
            "productcart_set",
        )
