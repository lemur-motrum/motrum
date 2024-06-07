from django import forms
from django.contrib import admin

from apps.product.models import Product
from apps.specification.forms import PersonForm
from apps.specification.models import ProductSpecification, Specification
from apps.specification.utils import crete_pdf_specification


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    form = PersonForm
    can_delete = False
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
        obj.save()
        super(SpecificationAdmin, self).save_related(request, form, formsets, change)


class SpecificationAdmin(admin.ModelAdmin):
    search_fields = [
        "id_bitrix",
    ]
    list_display = ["id_bitrix", "date", "admin_creator", "total_amount", "tag_stop"]
    inlines = [ProductSpecificationInline]
    fieldsets = [
        (
            "Основные параметры",
            {
                "fields": [
                    ("id_bitrix", "date", "admin_creator", "total_amount", "tag_stop"),
                    "file",
                ],
            },
        ),
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["id_bitrix", "date", "admin_creator", "total_amount", "tag_stop"]
        return ["date", "admin_creator", "total_amount", "tag_stop"]

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

    def save_related(self, request, form, formsets, change):
        super(SpecificationAdmin, self).save_related(request, form, formsets, change)
        id_sec = form.instance.id
        pdf = crete_pdf_specification(id_sec)
        print(pdf)
        Specification.objects.filter(id=form.instance.id).update(file=pdf)

    def save_model(self, request, obj, form, change):
        obj.admin_creator = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(admin_creator=request.user)


admin.site.register(Specification, SpecificationAdmin)

