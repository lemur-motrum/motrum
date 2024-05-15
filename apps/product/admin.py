from django.contrib import admin

from apps.product.models import (
    CategoryProduct,
    GroupProduct,
    Lot,
    Price,
    Product,
    ProductDocument,
    ProductImage,
    ProductProperty,
    Stock,
)


# Register your models here.
class GroupProductInline(admin.TabularInline):
    model = GroupProduct
    fields = ("name",)


class SupplierAdmin(admin.ModelAdmin):
    fields = ("name",)

    inlines = [
        GroupProductInline,
    ]


class GroupProductAdmin(admin.ModelAdmin):
    list_display = ("name",)


class LotAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "name_shorts",
    )


class PriceInline(admin.TabularInline):
    model = Price
    fields = (
        "currency",
        "vat",
        "rub_price_supplier",
        "price_motrum",
    )


class StockInline(admin.TabularInline):
    model = Stock
    fields = (
        "stock_supplier",
        "lot",
        "lot_complect",
        "stock_supplier_unit",
        "stock_motrum",
    )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ("photo",)


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    fields = ("document",)


class ProductPropertyInline(admin.TabularInline):
    model = ProductProperty
    fields = (
        "name",
        "value",
    )


class ProductAdmin(admin.ModelAdmin):
    list_filter = [
        "supplier",
    ]
    list_display = [
        "article",
        "article_supplier",
        # "supplier",
        # "vendor",
        # "name",
        # "price",
    ]
    list_editable = (
        # "name",
        # "price",
    )
    inlines = [
        PriceInline,
        StockInline,
        ProductPropertyInline,
        ProductDocumentInline,
        ProductImageInline,
    ]

    fieldsets = [
        (
            "Основные параметры",
            {
                "fields": [
                    ("supplier", "vendor"),
                    "article_supplier",
                    "additional_article_supplier",
                    ("category", "group"),
                    "name",
                    "description",
                ],
            },
        ),
        (
            "Характеристики",
            {
                "classes": ["wide"],
                "fields": ["check_image_upgrade", "check_document_upgrade"],
            },
        ),
    ]


admin.site.register(CategoryProduct, SupplierAdmin)
admin.site.register(GroupProduct, GroupProductAdmin)
admin.site.register(Lot, LotAdmin)
admin.site.register(Product, ProductAdmin)
