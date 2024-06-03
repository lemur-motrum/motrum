from django import forms
from django.contrib import admin

from apps.product.models import Product
from apps.specification.forms import PersonForm
from apps.specification.models import ProductSpecification, Specification
from apps.specification.utils import crete_pdf_specification


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    form = PersonForm
    # extra = 1
    can_delete = False

    # fields = [
    #     "supplier",
    #     "vendor",
    #     "product",
    #     "quantity",
    # ]
    fieldsets = [
        (
            None,
            {
                "fields": ["product", "quantity", "price_one", "price_all"],
            },
        ),
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["product", "quantity", "price_one", "price_all"]
        return []

    def get_fieldsets(self, request, obj):
        fields = super(ProductSpecificationInline, self).get_fieldsets(request, obj)
        fields_add = [
            (
                None,
                {
                    "fields": [
                        ("supplier", "vendor"),
                    ],
                },
            ),
            (
                None,
                {
                    "fields": ["product", "quantity"],
                },
            ),
        ]
        if obj and obj.pk:
            return fields
        else:
            return fields_add

    def get_extra(self, request, obj=None, **kwargs):
        extra = 1
        if obj:
            extra = 0
            return extra
        return extra

    def has_add_permission(self, request, obj):
        if obj:
            return False
        return True
    def save_related(self, request, form, formsets, change):
        obj = form.instance
        print(obj.id)
        print(obj.total_amount)
        # make changes to model instance
        obj.save()
        super(SpecificationAdmin, self).save_related(request, form, formsets, change)   

    # def response_add(self, request, obj, post_url_continue=None):
    #     print(234234234)
    #     print(obj.id)
    #     return super(ProductSpecificationInline, self).response_add(request, obj)


class SpecificationAdmin(admin.ModelAdmin):
    search_fields = [
        "id_bitrix",
    ]
    list_display = [
        "id_bitrix",
        "date",
        "admin_creator",
        "total_amount",
    ]
    inlines = [ProductSpecificationInline]
    fieldsets = [
        (
            "Основные параметры",
            {
                "fields": [
                    ("id_bitrix", "date", "admin_creator", "total_amount"),
                ],
            },
        ),
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["id_bitrix", "date"]
        return [
            "date",
        ]

    def get_fieldsets(self, request, obj):
        fields = super(SpecificationAdmin, self).get_fieldsets(request, obj)
        fields_add = [
            (
                "Основные параметры",
                {
                    "fields": [
                        ("id_bitrix", "date"),
                    ],
                },
            ),
        ]
        if obj and obj.pk:
            return fields
        else:
            return fields_add

    # def save_related(self, request, form, formsets, change):
    #     obj = form.instance
    #     print(obj.id)
    #     print(obj.total_amount)
    #     # make changes to model instance
    #     obj.save()
    #     super(SpecificationAdmin, self).save_related(request, form, formsets, change)   
    def save_related(self, request, form, formsets, change):
        super(SpecificationAdmin, self).save_related( request, form, formsets, change)
        id_sec =form.instance.id
        crete_pdf_specification(id_sec)
        # print(ProductSpecification.objects.filter(specification=id_sec))
        # form in formsets()
        # form_object = form.instance.save()
        
       
      



admin.site.register(Specification, SpecificationAdmin)
# admin.site.register(ProductSpecification, ProductSpecificationAdmin)
