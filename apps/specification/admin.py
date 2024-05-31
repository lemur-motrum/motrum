from django import forms
from django.contrib import admin

from apps.product.models import Product
from apps.specification.forms import PersonForm
from apps.specification.models import ProductSpecification, Specification


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    form = PersonForm
    extra = 1
    fields = ["supplier","vendor","product", "quantity",]
    

class SpecificationAdmin(admin.ModelAdmin):
    search_fields = [
        "id_bitrix",
    ]
    inlines = [ProductSpecificationInline]
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
    
class ProductSpecificationAdmin(admin.ModelAdmin):
    form = PersonForm



admin.site.register(Specification, SpecificationAdmin)
admin.site.register(ProductSpecification,ProductSpecificationAdmin)
