import datetime
from itertools import chain
from django import http
from django.conf import settings
from django.utils import timezone
from os import path
from django import forms
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from apps.core.utils import create_time_stop_specification, send_email_error
from apps.product.models import Price, Product
from apps.specification.forms import PersonForm
from apps.specification.models import ProductSpecification, Specification
from apps.specification.utils import crete_pdf_specification
from django.utils.html import format_html
from django.db.models import Count, Sum
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.auth import get_permission_codename, get_user_model
from django.utils.text import capfirst
from django.utils.encoding import force_str
from django.core.exceptions import PermissionDenied
from django.contrib.admin.utils import unquote
from django.db.models import Q

SIMPLE_HISTORY_EDIT = getattr(settings, "SIMPLE_HISTORY_EDIT", False)


class ProductSpecificationAdmin(SimpleHistoryAdmin):
    model = ProductSpecification

    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""

        model = ProductSpecification
        opts = model._meta

        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)

        object_id = object_id

        historical_records = ProductSpecificationAdmin.get_history_queryset(
            ProductSpecificationAdmin, request, history, pk_name, object_id
        )

        history_list_display = ProductSpecificationAdmin.get_history_list_display(
            ProductSpecificationAdmin, request
        )

        for history_list_entry in history_list_display:
            value_for_entry = getattr(self, history_list_entry, None)
            if value_for_entry and callable(value_for_entry):
                for record in historical_records:
                    setattr(record, history_list_entry, value_for_entry(record))

        ProductSpecificationAdmin.set_history_delta_changes(
            ProductSpecificationAdmin, request, historical_records
        )

        return historical_records

    def set_history_delta_changes(
        self,
        request,
        historical_records,
        foreign_keys_are_objs=True,
    ):
        previous = None
        for current in historical_records:
            if previous is None:
                previous = current
                continue
            # Related objects should have been prefetched in `get_history_queryset()`
            delta = previous.diff_against(
                current, foreign_keys_are_objs=foreign_keys_are_objs
            )

            helper = ProductSpecificationAdmin.get_historical_record_context_helper(
                ProductSpecificationAdmin, request, previous
            )
            previous.history_delta_changes = helper.context_for_delta_changes(delta)

            previous = current


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    form = PersonForm

    fieldsets = [
        (
            None,
            {
                "fields": [
                    "product",
                    "quantity",
                    "price_one",
                    "price_all",
                    "extra_discount",
                ],
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
                return [
                    "product",
                    "quantity",
                    "price_one",
                    "price_all",
                    "extra_discount",
                ]
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


class SpecificationAdmin(SimpleHistoryAdmin):
    object_history_list_template = "specification/templates_history.html"
    history_list_display = []
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
            date_stop = create_time_stop_specification()

            obj.date = date
            obj.date_stop = date_stop
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(admin_creator=request.user)

    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""
        request.current_app = self.admin_site.name

        model = self.model
        opts = model._meta
        app_label = opts.app_label
        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)

        object_id = unquote(object_id)

        try:
            product_id_ex = ProductSpecification.objects.filter(
                specification=object_id
            ).last()
            product_id = ProductSpecification.objects.filter(specification=object_id)

        except ProductSpecification.DoesNotExist:
            product_id = None

        historical_records_product = []
        if product_id != None:
            for item in product_id:
                item_list = ProductSpecificationAdmin.history_view(
                    ProductSpecification, request, item.id, extra_context=None
                )
                if historical_records_product == []:
                    historical_records_product = item_list
                else:
                    historical_records_product = list(
                        chain(
                            historical_records_product,
                            item_list,
                        )
                    )

        deleted_prod = ProductSpecification.history.filter(history_type="-", specification_id=object_id)

        historical_records_product2 = []
        id_old_prod = []
        for item2 in deleted_prod:
            id_old_prod.append(item2.id)
            item_list = ProductSpecificationAdmin.history_view(
                ProductSpecification, request, item2.id, extra_context=None
            )

            if historical_records_product2 == []:
                historical_records_product2 = item_list
            else:
                historical_records_product2 = list(
                    chain(
                        historical_records_product2,
                        item_list,
                    )
                )
        
        

        historical_records = self.get_history_queryset(
            request, history, pk_name, object_id
        )

        history_list_display = self.get_history_list_display(request)

        # If no history was found, see whether this object even exists.
        try:
            obj = self.get_queryset(request).get(**{pk_name: object_id})
        except model.DoesNotExist:
            try:
                obj = historical_records.latest("history_date").instance
            except historical_records.model.DoesNotExist:
                raise http.Http404

        if not self.has_view_history_or_change_history_permission(request, obj):
            raise PermissionDenied

        # Set attribute on each historical record from admin methods
        for history_list_entry in history_list_display:
            value_for_entry = getattr(self, history_list_entry, None)
            if value_for_entry and callable(value_for_entry):
                for record in historical_records:
                    setattr(record, history_list_entry, value_for_entry(record))

        self.set_history_delta_changes(request, historical_records)

        result_list = list(
            chain(
                historical_records,
                historical_records_product,
                historical_records_product2,
            )
        )

        def get_date(element):
            return element.history_date

        result_list_sorted = result_list.sort(key=get_date, reverse=True)

        content_type = self.content_type_model_cls.objects.get_for_model(
            get_user_model()
        )
        admin_user_view = "admin:{}_{}_change".format(
            content_type.app_label,
            content_type.model,
        )

        context = {
            "title": self.history_view_title(request, obj),
            "object_history_list_template": self.object_history_list_template,
            "historical_records": result_list,
            "module_name": capfirst(force_str(opts.verbose_name_plural)),
            "object": obj,
            "root_path": getattr(self.admin_site, "root_path", None),
            "app_label": app_label,
            "opts": opts,
            "admin_user_view": admin_user_view,
            "history_list_display": history_list_display,
            "revert_disabled": self.revert_disabled(request, obj),
        }
        context.update(self.admin_site.each_context(request))

        context.update(extra_context or {})
        extra_kwargs = {}
        return self.render_history_view(
            request, self.object_history_template, context, **extra_kwargs
        )

    def has_add_permission(self, request):
        return False


admin.site.register(Specification, SpecificationAdmin)
