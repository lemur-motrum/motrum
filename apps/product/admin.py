from django.contrib import admin

# from myapp.models import MyModel
# from myapp.widgets import RichTextEditorWidget
from apps.product.forms import ProductForm
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
        "vat_include",
        "price_supplier",
        "rub_price_supplier",
        "price_motrum",
        "sale",
    )
    readonly_fields = ["rub_price_supplier", "price_motrum", "sale"]


class StockInline(admin.TabularInline):
    model = Stock
    fields = (
        "lot",
        "stock_supplier",
        "lot_complect",
        "stock_supplier_unit",
        "stock_motrum",
    )

    readonly_fields = ["stock_supplier_unit"]


class ProductImageAdmin(admin.ModelAdmin):
    fields = (
        "photo",
        "file",
        "link",
    )


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ("photo",)
    extra = 0
    # def has_delete_permission(self, request, obj=None):
    #     return True


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    fields = ("document","type_doc")
    extra = 0


class ProductPropertyInline(admin.TabularInline):
    model = ProductProperty
    fields = (
        "name",
        "value",
    )
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS
    form = ProductForm
    search_fields = [
        "article",
        "article_supplier",
        "additional_article_supplier",
        "name",
    ]
    search_help_text = "Поиск может осуществляться по: Артикулу Motrum, Артикулу поставщика,Дополнительному артикулу, Названию товара"
    list_filter = ["supplier", "category", "group"]
    list_display = [
        "article",
        "article_supplier",
        "additional_article_supplier",
        "supplier",
        "vendor",
        "name",
    ]

    inlines = [
        PriceInline,
        StockInline,
        ProductPropertyInline,
        ProductImageInline,
        ProductDocumentInline,
    ]
    # formfield_overrides = {
    #     models.TextField: {"widget": RichTextEditorWidget},
    # }
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
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [
                "article_supplier",
                "supplier"
            ]
        return [
            "",
        ]

    def get_fieldsets(self, request, obj):
        fields = super(ProductAdmin, self).get_fieldsets(request, obj)
        fields_add = [
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
        ]
        if obj and obj.pk:
            return fields
        else:
            return fields_add

    # def save_model(self, request, obj, form, change):
    #     print(obj)
    #     print(self)

    #     print(change)
    #     obj.user = request.user
    #     super().save_model(request, obj, form, change)


admin.site.register(CategoryProduct, SupplierAdmin)
admin.site.register(GroupProduct, GroupProductAdmin)
admin.site.register(Lot, LotAdmin)
admin.site.register(Product, ProductAdmin)
