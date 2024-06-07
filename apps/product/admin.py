from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

# from myapp.models import MyModel
# from myapp.widgets import RichTextEditorWidget
# from apps.product.forms import ProductForm
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


# class GroupProductAdmin(admin.ModelAdmin):
#     fields = ("name",)

#     inlines = [
#         GroupProductInline,
#     ]


class GroupProductAdmin(admin.ModelAdmin):
    list_display = ("name",)


class LotAdmin(admin.ModelAdmin):
    fields = (
        "name",
        "name_shorts",
    )


class PriceInline(admin.TabularInline):
    model = Price
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
    history_list_display = ["price_supplier"]
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
    
    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""
        request.current_app = self.admin_site.name
        model = self.model
        opts = model._meta
        
        app_label = opts.app_label
        pk_name = opts.pk.attname
        history = getattr(model, model._meta.simple_history_manager_attribute)
        object_id = unquote(object_id)
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
                    print(setattr(record, history_list_entry, value_for_entry(record)))

        self.set_history_delta_changes(request, historical_records)

        content_type = self.content_type_model_cls.objects.get_for_model(
            get_user_model()
        )
        admin_user_view = "admin:{}_{}_change".format(
            content_type.app_label,
            content_type.model,
        )
        print()
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
        context.update(self.admin_site.each_context(request))
        context.update(extra_context or {})
        extra_kwargs = {}
        return self.render_history_view(
            request, self.object_history_template, context, **extra_kwargs
        )


    def get_history_queryset(
        self, request, history_manager, pk_name, object_id
    ):
        """
        Return a ``QuerySet`` of all historical records that should be listed in the
        ``object_history_list_template`` template.
        This is used by ``history_view()``.

        :param request:
        :param history_manager:
        :param pk_name: The name of the original model's primary key field.
        :param object_id: The primary key of the object whose history is listed.
        """
        print(object_id)
        qs = history_manager.filter(**{pk_name: object_id})
        # qs_price = Price.objects.filter(**{"prod": object_id})
        print()
        for q in qs:
            print()
        if not isinstance(history_manager.model.history_user, property):
            # Only select_related when history_user is a ForeignKey (not a property)
            qs = qs.select_related("history_user")
        # Prefetch related objects to reduce the number of DB queries when diffing
        qs = qs._select_related_history_tracked_objs()
     
        return qs
   

admin.site.register(CategoryProduct, GroupProductAdmin)
admin.site.register(GroupProduct, GroupProductAdmin)
admin.site.register(Lot, LotAdmin)
admin.site.register(Product, ProductAdmin)


