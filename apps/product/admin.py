from django.utils import timezone
from django.contrib import admin
from django.contrib.admin import helpers
from django.urls import re_path, reverse
from django.utils.html import mark_safe
from simple_history.admin import SimpleHistoryAdmin
from itertools import chain
from simple_history.template_utils import HistoricalRecordContextHelper
from django.contrib import admin

from django.utils.translation import gettext as _
from django.conf import settings
from simple_history.utils import (
    get_history_manager_for_model,
    get_history_model_for_model,
)
from django.forms import TextInput, Textarea
from simple_history.utils import update_change_reason

from apps.core.utils import create_article_motrum
from project.settings import MEDIA_URL


SIMPLE_HISTORY_EDIT = getattr(settings, "SIMPLE_HISTORY_EDIT", False)
# from myapp.models import MyModel
# from myapp.widgets import RichTextEditorWidget
# from apps.product.forms import ProductForm
from simple_history.manager import HistoricalQuerySet, HistoryManager
from . import models
from apps.product.forms import ProductChangeForm, ProductForm
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
from django.shortcuts import get_object_or_404, render
from apps.supplier.models import (
    SupplierCategoryProduct,
    SupplierCategoryProductAll,
    SupplierGroupProduct,
    Vendor,
)
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django import http
from django.contrib.auth import get_permission_codename, get_user_model
from django.utils.text import capfirst
from django.utils.encoding import force_str







class StockAdmin(SimpleHistoryAdmin):
    model = Stock

    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""
        model = self.model
        opts = model._meta

        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)
        object_id = object_id

        historical_records = StockAdmin.get_history_queryset(
            StockAdmin, request, history, pk_name, object_id
        )

        history_list_display = StockAdmin.get_history_list_display(StockAdmin, request)

        for history_list_entry in history_list_display:
            value_for_entry = getattr(self, history_list_entry, None)
            if value_for_entry and callable(value_for_entry):
                for record in historical_records:
                    setattr(record, history_list_entry, value_for_entry(record))

        StockAdmin.set_history_delta_changes(StockAdmin, request, historical_records)

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
            helper = StockAdmin.get_historical_record_context_helper(
                StockAdmin, request, previous
            )
            previous.history_delta_changes = helper.context_for_delta_changes(delta)

            previous = current


class PriceAdmin(SimpleHistoryAdmin):
    model = Price

    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""

        model = self.model
        opts = model._meta

        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)
        object_id = object_id

        historical_records = PriceAdmin.get_history_queryset(
            PriceAdmin, request, history, pk_name, object_id
        )

        history_list_display = PriceAdmin.get_history_list_display(PriceAdmin, request)

        # Set attribute on each historical record from admin methods
        for history_list_entry in history_list_display:
            value_for_entry = getattr(self, history_list_entry, None)
            if value_for_entry and callable(value_for_entry):
                for record in historical_records:
                    setattr(record, history_list_entry, value_for_entry(record))

        PriceAdmin.set_history_delta_changes(PriceAdmin, request, historical_records)

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
            helper = PriceAdmin.get_historical_record_context_helper(
                PriceAdmin, request, previous
            )
            previous.history_delta_changes = helper.context_for_delta_changes(delta)

            previous = current


class ProductPropertyAdmin(SimpleHistoryAdmin):
    model = ProductProperty

    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""

        model = self.model
        opts = model._meta
        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)
        object_id = object_id

        historical_records = ProductPropertyAdmin.get_history_queryset(
            ProductPropertyAdmin, request, history, pk_name, object_id
        )

        history_list_display = ProductPropertyAdmin.get_history_list_display(
            ProductPropertyAdmin, request
        )

        for history_list_entry in history_list_display:
            value_for_entry = getattr(self, history_list_entry, None)
            if value_for_entry and callable(value_for_entry):
                for record in historical_records:
                    setattr(record, history_list_entry, value_for_entry(record))

        ProductPropertyAdmin.set_history_delta_changes(
            ProductPropertyAdmin, request, historical_records
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
            helper = ProductPropertyAdmin.get_historical_record_context_helper(
                ProductPropertyAdmin, request, previous
            )
            previous.history_delta_changes = helper.context_for_delta_changes(delta)

            previous = current


class ProductImageAdmin(SimpleHistoryAdmin):
    model = ProductImage

    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""
        model = self.model
        opts = model._meta
        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)
        object_id = object_id

        historical_records = ProductImageAdmin.get_history_queryset(
            ProductImageAdmin, request, history, pk_name, object_id
        )

        history_list_display = ProductImageAdmin.get_history_list_display(
            ProductImageAdmin, request
        )
        # Set attribute on each historical record from admin methods
        for history_list_entry in history_list_display:
            value_for_entry = getattr(self, history_list_entry, None)
            if value_for_entry and callable(value_for_entry):
                for record in historical_records:
                    setattr(record, history_list_entry, value_for_entry(record))

        ProductImageAdmin.set_history_delta_changes(
            ProductImageAdmin, request, historical_records
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
            helper = ProductImageAdmin.get_historical_record_context_helper(
                ProductImageAdmin, request, previous
            )
            previous.history_delta_changes = helper.context_for_delta_changes(delta)

            previous = current


class ProductDocumentAdmin(SimpleHistoryAdmin):
    model = ProductDocument

    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""
        # request.current_app = self.admin_site.name

        model = self.model
        opts = model._meta
        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)
        object_id = object_id
        historical_records = ProductDocumentAdmin.get_history_queryset(
            ProductDocumentAdmin, request, history, pk_name, object_id
        )

        history_list_display = ProductDocumentAdmin.get_history_list_display(
            ProductDocumentAdmin, request
        )

        # Set attribute on each historical record from admin methods
        for history_list_entry in history_list_display:
            value_for_entry = getattr(self, history_list_entry, None)
            if value_for_entry and callable(value_for_entry):
                for record in historical_records:
                    setattr(record, history_list_entry, value_for_entry(record))

        ProductDocumentAdmin.set_history_delta_changes(
            ProductDocumentAdmin, request, historical_records
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
            helper = ProductDocumentAdmin.get_historical_record_context_helper(
                ProductDocumentAdmin, request, previous
            )
            previous.history_delta_changes = helper.context_for_delta_changes(delta)

            previous = current


class GroupProductAdmin(admin.ModelAdmin):
    list_display = ("name",)



class PriceInline(admin.TabularInline):
    model = Price
    min_num = 1
    fields = (
        "currency",
        "vat",
        # "vat_include",
        "extra_price",
        "price_supplier",
        "rub_price_supplier",
        "price_motrum",
        "sale",
    )
    readonly_fields = ["rub_price_supplier", "price_motrum", "sale"]

    def __init__(self, *args, **kwargs):
        super(PriceInline, self).__init__(*args, **kwargs)
        self.can_delete = False


class StockInline(admin.TabularInline):
    model = Stock
    min_num = 1
    fields = (
        "lot",
        "stock_supplier",
        "lot_complect",
        "stock_supplier_unit",
        "stock_motrum",
    )

    readonly_fields = ["stock_supplier_unit"]

    def __init__(self, *args, **kwargs):
        super(StockInline, self).__init__(*args, **kwargs)
        self.can_delete = False


class ProductImageInline(admin.TabularInline):
    model = ProductImage

    extra = 0
    fields = (
        "preview",
        "photo",
        "hide",
    )

    def preview(self, obj):
        print(obj.photo.url)
        img = mark_safe(
            '<img src="{}" height="100"  />'.format(obj.photo.url)
        )
        return img

    def __init__(self, *args, **kwargs):
        super(ProductImageInline, self).__init__(*args, **kwargs)
        self.can_delete = False

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.filter(hide=False)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["preview",]
        return [
            "preview",
        ]

    def get_fields(self, request, obj=None):
        print(request)
        if obj:
            return [
                "preview",
                "photo",
                "hide",
            ]
        return [
            "photo",
        ]


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    fields = ("document", "type_doc", "hide")
    extra = 0

    def __init__(self, *args, **kwargs):
        super(ProductDocumentInline, self).__init__(*args, **kwargs)
        self.can_delete = False

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.filter(hide=False)


class ProductPropertyInline(admin.TabularInline):
    model = ProductProperty
    fields = ("name", "value", "hide")
    extra = 0

    def __init__(self, *args, **kwargs):
        super(ProductPropertyInline, self).__init__(*args, **kwargs)
        self.can_delete = False

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        return qs.filter(hide=False)


class ProductAdmin(SimpleHistoryAdmin):
    show_facets = admin.ShowFacets.ALWAYS
    form = ProductChangeForm
    object_history_list_template = "product/templates_history.html"
    history_list_display = []
    search_fields = [
        "article",
        "article_supplier",
        "additional_article_supplier",
        "name",
    ]
    search_help_text = "Поиск может осуществляться по: Артикулу Motrum, Артикулу поставщика,Дополнительному артикулу, Названию товара"
    list_filter = ["supplier", "vendor", "category", "group"]
    list_display = [
        "article",
        "article_supplier",
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

    fieldsets = [
        (
            "Основные параметры",
            {
                "fields": [
                    (
                        "article_supplier",
                        "additional_article_supplier",
                    ),
                    "name",
                    "description",
                    ("supplier", "vendor"),
                    ("category_supplier", "group_supplier", "category_supplier_all"),
                    ("category", "group"),
                ],
            },
        ),
    ]


    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     if request.user.username[0].upper() != "J":
    #         if "delete_selected" in actions:
    #             del actions["delete_selected"]
    #     return actions

    def delete_queryset(self, request, queryset):
        for obj in queryset.all():
            obj.delete()

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["article_supplier", "supplier"]
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
                        (
                            "article_supplier",
                            "additional_article_supplier",
                        ),
                        "name",
                        "description",
                        ("supplier", "vendor"),
                        (
                            "category_supplier",
                            "group_supplier",
                            "category_supplier_all",
                        ),
                        ("category", "group"),
                    ],
                },
            ),
        ]
        if obj and obj.pk:
            return fields
        else:
            return fields_add

    def has_add_permission(self, request):
        if request.path == "/admin/specification/specification/add/":
            return False
        else:
            return True

    def get_form(self, request, obj, **kwargs):
        if obj == None:
            kwargs["form"] = ProductForm
        return super().get_form(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):

        if "/change/" in request.path:

            for id_table in request.resolver_match.captured_kwargs.values():
                parent_id = id_table

            item = Product.objects.get(id=parent_id)

            if db_field.name == "vendor":
                kwargs["queryset"] = Vendor.objects.filter(supplier_id=item.supplier.id)
            if db_field.name == "category_supplier_all":
                kwargs["queryset"] = SupplierCategoryProductAll.objects.filter(
                    supplier_id=item.supplier.id, vendor_id=item.vendor.id
                )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        obj._change_reason = "Ручное"
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save()
        for instance in instances:
            update_change_reason(instance, "Ручное")
            instance.save()
    # история изменений
    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""
        request.current_app = self.admin_site.name

        model = self.model
        opts = model._meta
        app_label = opts.app_label
        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)

        object_id = unquote(object_id)
        stock_id = Stock.objects.get(prod=object_id)

        price_id = Price.objects.get(prod=object_id)
        property_id = ProductProperty.objects.filter(product=object_id)

        image_id = ProductImage.objects.filter(product=object_id)
        doc_id = ProductDocument.objects.filter(product=object_id)

        historical_records_property = []
        for property_item in property_id:
            property_list = ProductPropertyAdmin.history_view(
                ProductPropertyAdmin, request, property_item.id, extra_context=None
            )
            if historical_records_property == []:
                historical_records_property = property_list
            else:
                historical_records_property = list(
                    chain(
                        historical_records_property,
                        property_list,
                    )
                )

        historical_records_image = []
        for item in image_id:
            item_list = ProductImageAdmin.history_view(
                ProductImageAdmin, request, item.id, extra_context=None
            )
            if historical_records_image == []:
                historical_records_image = item_list
            else:
                historical_records_image = list(
                    chain(
                        historical_records_image,
                        item_list,
                    )
                )

        historical_records_doc = []
        for item in doc_id:
            item_list = ProductDocumentAdmin.history_view(
                ProductDocumentAdmin, request, item.id, extra_context=None
            )
            if historical_records_doc == []:
                historical_records_doc = item_list
            else:
                historical_records_doc = list(
                    chain(
                        historical_records_doc,
                        item_list,
                    )
                )

        historical_records = self.get_history_queryset(
            request, history, pk_name, object_id
        )
        historical_records_stock = StockAdmin.history_view(
            StockAdmin, request, stock_id.id, extra_context=None
        )
        historical_records_price = PriceAdmin.history_view(
            PriceAdmin, request, price_id.id, extra_context=None
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
                historical_records_stock,
                historical_records_price,
                historical_records_property,
                historical_records_image,
                historical_records_doc,
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

class LotAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "name_shorts",
    )

class GroupProductInline(admin.TabularInline):
    model = GroupProduct
    fields = (
        "name",
    )
    
    


class CategoryProductAdmin(admin.ModelAdmin):
    fields = ("name","get_name")
    list_display = ['name', 'get_name', ]
    inlines = [
        GroupProductInline,
    ]
    
    def get_name(self, obj):
        group = GroupProduct.objects.filter(category=obj)
        print(12313)
        return group
    # get_name.admin_order_field  = 'author'  #Allows column order sorting
    # get_name.short_description = 'Author Name'  #Renames column head


admin.site.register(CategoryProduct,CategoryProductAdmin)
admin.site.register(GroupProduct)

admin.site.register(Product, ProductAdmin)
# admin.site.register(Lot)
