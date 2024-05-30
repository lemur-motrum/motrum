from django.contrib import admin

from apps.product.models import Product
from apps.specification.models import ProductSpecification, Specification

# Register your models here.
# class ProductInline(admin.TabularInline):
#     model = Product
#     fields = (
#         "supplier",
#         "vendor",
#     )
class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
  
    fields = (
        "product",
        "quantity",
    )
    extra = 1
# class ProductSpecificationAdmin(admin.ModelAdmin):
#     # inlines = [
#     #     ProductInline
#     # ]
#     # list_display = ("name",)

    
class SpecificationAdmin(admin.ModelAdmin):
    search_fields = [
        'id_bitrix',
    ]
    inlines = [
        ProductSpecificationInline
    ]
    fieldsets = [
        (
            "Основные параметры",
            {
                "fields": [
                    ("id_bitrix",),
                   
                ],
            },
        ),
    ]
    # list_display = ("name",)


admin.site.register(Specification, SpecificationAdmin)
admin.site.register(ProductSpecification)