from django.contrib import admin

from apps.specification.models import ProductSpecification, Specification

# Register your models here.
class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    fields = (
        "product",
        "quantity",
    )
    extra = 1
class SpecificationAdmin(admin.ModelAdmin):
    inlines = [
        ProductSpecificationInline,
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