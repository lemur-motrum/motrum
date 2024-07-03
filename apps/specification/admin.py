import datetime
from django.utils import timezone
from os import path
from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from apps.core.utils import create_time, send_email_error
from apps.product.models import Price, Product
from apps.specification.forms import PersonForm
from apps.specification.models import ProductSpecification, Specification
from apps.specification.utils import crete_pdf_specification
from django.utils.html import format_html
from django.db.models import Count, Sum


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    form = PersonForm

    fieldsets = [
        (
            None,
            {
                "fields": ["product", "quantity", "price_one", "price_all"],
            },
        ),
    ]

    def get_readonly_fields(self, request, obj=None):
        # если спецификация недействительна пресчет

        if obj:
            for id_table in request.resolver_match.captured_kwargs.values():
                parent_id = id_table

            spec = Specification.objects.get(id=parent_id)
            if spec.tag_stop == False:

                return ["quantity", "price_all"]
            else:
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
                    "fields": [
                        "product",
                        "quantity",
                        "price_one",
                    ],
                },
            ),
        ]
        fields_change = [
            (
                None,
                {
                    "fields": [
                        "product",
                        "quantity",
                        "price_one",
                    ],
                },
            ),
        ]
        if obj and obj.pk:
            for id_table in request.resolver_match.captured_kwargs.values():
                parent_id = id_table
                spec = Specification.objects.get(id=parent_id)
            if spec.tag_stop == False:

                return fields_change
            else:
                return fields
        else:
            return fields_add

        return super().get_form(request, obj, **kwargs)

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


class SpecificationAdmin(admin.ModelAdmin):

    search_fields = [
        "id_bitrix",
    ]
    list_display = [
        "id_bitrix",
        "date",
        "admin_creator",
        "total_amount",
        "tag_stop",
    ]
    inlines = [ProductSpecificationInline]
    fieldsets = [
        (
            "Основные параметры",
            {
                "fields": [
                    (
                        "id_bitrix",
                        "date",
                        "admin_creator",
                        "total_amount",
                        "tag_stop",
                    ),
                    "file",
                ],
            },
        ),
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.tag_stop == False:
                return [
                    "id_bitrix",
                ]
            else:
                return [
                    "id_bitrix",
                    "date",
                    "admin_creator",
                    "total_amount",
                    "tag_stop",
                ]

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
            if obj.tag_stop == False:
                fields_change = [
                    (
                        "Основные параметры",
                        {
                            "fields": [
                                (
                                    "id_bitrix",
                                    "date",
                                ),
                            ],
                        },
                    ),
                ]
                return fields_change
            else:
                return fields
        else:
            return fields_add

    def save_related(self, request, form, formsets, change):

        super(SpecificationAdmin, self).save_related(request, form, formsets, change)
        id_sec = form.instance.id

        sums = ProductSpecification.objects.filter(specification=id_sec).aggregate(
            Sum("price_all")
        )
        spes = Specification.objects.get(id=id_sec)
        spes.total_amount = sums["price_all__sum"]
        spes.save()

        pdf = crete_pdf_specification(id_sec)
        Specification.objects.filter(id=form.instance.id).update(file=pdf)

    def save_model(self, request, obj, form, change):

        obj.admin_creator = request.user
        if change:
            obj.tag_stop = True
            obj.total_amount = 0
            date = timezone.now()
            date_stop = create_time()

            obj.date = date
            obj.date_stop = date_stop
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(admin_creator=request.user)


admin.site.register(Specification, SpecificationAdmin)
