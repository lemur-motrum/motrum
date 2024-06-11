from django.utils import timezone
from django.contrib import admin
from django.contrib.admin import helpers
from django.urls import re_path, reverse
from django.utils.html import mark_safe
from simple_history.admin import SimpleHistoryAdmin
from itertools import chain
from simple_history.template_utils import HistoricalRecordContextHelper
from django.contrib import admin
from reversion.admin import VersionAdmin
from django.utils.translation import gettext as _
from django.conf import settings
from simple_history.utils import get_history_manager_for_model, get_history_model_for_model


SIMPLE_HISTORY_EDIT = getattr(settings, "SIMPLE_HISTORY_EDIT", False)
# from myapp.models import MyModel
# from myapp.widgets import RichTextEditorWidget
# from apps.product.forms import ProductForm
from simple_history.manager import HistoricalQuerySet, HistoryManager
from . import models
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
from django.shortcuts import get_object_or_404, render
from apps.supplier.models import SupplierCategoryProduct, SupplierCategoryProductAll, SupplierGroupProduct, Vendor
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django import http
from django.contrib.auth import get_permission_codename, get_user_model
from django.utils.text import capfirst
from django.utils.encoding import force_str
# Register your models here.
# class SupplierCategoryProductInline(admin.TabularInline):
#     model = SupplierCategoryProduct
#     fields = ("name",)
    
# class SupplierGroupProductInline(admin.TabularInline):
#     model = SupplierGroupProduct
#     fields = ("name",)
    
class SupplierCategoryProductAllInline(admin.TabularInline):
    model = SupplierCategoryProductAll
    fields = ("name",)    
    
class GroupProductInline(admin.TabularInline):
    model = GroupProduct
    fields = ("name",)



class StockAdmin(SimpleHistoryAdmin):
    model = Stock
    
    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""
     
        request.current_app = self.admin_site.name
        # print(self.admin_site.name)
        model = self.model
        opts = model._meta
        app_label = opts.app_label
        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)
        object_id = unquote(object_id)
        historical_records = self.get_history_queryset(
            request, history, pk_name, object_id
        )
   
        # stock = Stock.objects.get(prod = object_id )
        # id_stock = stock.id
    
       
        # print(historical_records2)
         # <class 'apps.product.admin.ProductAdmin'>
   
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
            "historical_records": historical_records,
            "module_name": capfirst(force_str(opts.verbose_name_plural)),
            "object": obj,
            "root_path": getattr(self.admin_site, "root_path", None),
            "app_label": app_label,
            "opts": opts,
            "admin_user_view": admin_user_view,
            "history_list_display": history_list_display,
            "revert_disabled": self.revert_disabled(request, obj),
        }
        
        # yt = StockAdmin.history_view()
     
            # for rt in r.history_delta_changes:
            #     print(rt)
        
        context.update(self.admin_site.each_context(request))
        extra_context = StockAdmin.history_view(self, request, object_id,)
        extra_context = {}
        # context.update(extra_context )
        extra_kwargs = {}

        return self.render_history_view(
            request, self.object_history_template, context, **extra_kwargs
        )
    




class GroupProductAdmin(admin.ModelAdmin):
    list_display = ("name",)


class LotAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "name_shorts",
    )


class PriceInline(admin.TabularInline):
    model = Price
    # fk_name = "prod"
    min_num = 1
    # model = Product.history.model
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
    min_num = 1
    fields = (
        "lot",
        "stock_supplier",
        "lot_complect",
        "stock_supplier_unit",
        "stock_motrum",
    )

    readonly_fields = ["stock_supplier_unit"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ("photo",)
    extra = 0


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    fields = ("document", "type_doc")
    extra = 0


class ProductPropertyInline(admin.TabularInline):
    model = ProductProperty
    fields = (
        "name",
        "value",
    )
    extra = 0


class ProductAdmin(SimpleHistoryAdmin):
    show_facets = admin.ShowFacets.ALWAYS
    # form = ProductForm
    
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

    fieldsets = [
        (
            "Основные параметры",
            {
                "fields": [
                    "article_supplier",
                    "additional_article_supplier",
                    ("supplier", "vendor"),
                    "category_supplier_all",
                    ("category", "group"),
                    "name",
                    "description",
                ],
            },
        ),
    ]
    # history_list_display = ['changed_fields']

    # def changed_fields(self, obj):
    #     if obj.prev_record:
    #         delta = obj.diff_against(obj.prev_record)
    #         return delta.changed_fields
    #     return None

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
                        ("supplier", "vendor"),
                        "article_supplier",
                        "additional_article_supplier",
                        "category_supplier_all",
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
                kwargs["queryset"] = SupplierCategoryProductAll.objects.filter(supplier_id=item.supplier.id, vendor_id=item.vendor.id)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)
   
  
    

admin.site.register(CategoryProduct, GroupProductAdmin)
admin.site.register(GroupProduct, GroupProductAdmin)
admin.site.register(Lot, LotAdmin)
admin.site.register(Product, ProductAdmin)
# admin.site.register(models.Stock.history.model)
admin.site.register(Stock, StockAdmin)


