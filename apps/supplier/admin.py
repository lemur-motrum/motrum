from dataclasses import field
from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from simple_history.utils import update_change_reason
import threading
from apps.product.admin import GroupProductInline
from apps.product.models import CategoryProduct, GroupProduct, Price
from apps.supplier.forms import (
    DiscountForm,
    SupplierCategoryProductAdminForm,
    SupplierCategoryProductAllAdminForm,
    SupplierGroupProductAdminForm,
)
from apps.supplier.get_utils.avangard import get_avangard_file
from apps.supplier.get_utils.delta import add_delta_product, add_file_delta
from apps.supplier.get_utils.emas import (
    add_file_emas,
    add_group_emas,
    add_props_emas_product,
)
from apps.supplier.get_utils.instart import get_instart_file
from apps.supplier.get_utils.optimus import add_file_optimus, add_optimus_product

# Register your models here.
from .models import (
    Discount,
    Supplier,
    SupplierCategoryProduct,
    SupplierCategoryProductAll,
    SupplierGroupProduct,
    SupplierPromoGroupe,
    Vendor,
)
from django.utils.html import mark_safe
from project.admin import website_admin


class VendorInline(admin.TabularInline):
    model = Vendor
    fields = (
        "name",
        "currency_catalog",
        "vat_catalog",
    )


class SupplierAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            "Основные параметры",
            {
                "fields": [("name",)],
            },
        ),
    ]
    # readonly_fields = ["name",]
    
    # inlines = [
    #     VendorInline,
    # ]

    def get_fieldsets(self, request, obj):
        fields = super(SupplierAdmin, self).get_fieldsets(request, obj)

        fields_add = [
            (
                "Основные параметры",
                {
                    "fields": [("name", "file")],
                },
            ),
        ]
        if obj and obj.pk:
            if (
                obj.slug == "delta"
                or obj.slug == "optimus-drive"
                or obj.slug == "emas"
                or obj.slug == "avangard"
                or obj.slug == "instart"
            ):
                return fields_add

            else:
                return fields
        else:
            return fields

    def save_model(self, request, obj, form, change):

        if obj.id != None:
            old_supplier = Supplier.objects.get(id=obj.id)
            old_file = old_supplier.file

        super().save_model(request, obj, form, change)

        if obj.file:
            new_file = obj.file
            print(0000000000000)
            print(obj.file)

            if new_file != old_file:
                if old_supplier.slug == "delta":
                    new_dir = add_file_delta(new_file, obj)
                    daemon_thread = threading.Thread(target=add_delta_product)
                    daemon_thread.setDaemon(True)
                    daemon_thread.start()
                if old_supplier.slug == "optimus-drive":

                    new_dir = add_file_optimus(new_file, obj)
                    daemon_thread = threading.Thread(target=add_optimus_product)
                    daemon_thread.setDaemon(True)
                    daemon_thread.start()
                if old_supplier.slug == "emas":

                    def new_task():
                        add_file_emas(new_file, obj)

                    daemon_thread = threading.Thread(target=new_task)
                    daemon_thread.setDaemon(True)
                    daemon_thread.start()
                    # add_file_emas(new_file, obj) # добавление прайса
                    # add_group_emas(new_file) # добавление групп
                    # add_props_emas_product() # добавленеи пропсов

                if old_supplier.slug == "avangard":

                    def new_task():
                        get_avangard_file(new_file, obj)

                    daemon_thread = threading.Thread(target=new_task)
                    daemon_thread.setDaemon(True)
                    daemon_thread.start()
                
                if old_supplier.slug == "instart":

                    def new_task():
                        get_instart_file(new_file)

                    daemon_thread = threading.Thread(target=new_task)
                    daemon_thread.setDaemon(True)
                    daemon_thread.start()
                    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            
            return ["name",]
        else:
            return [
                "",
            ]

    def has_delete_permission(self, request, obj=None):
        return False


class SupplierVendor(admin.ModelAdmin):
    # list_display = ["supplier", "name", "currency_catalog", "vat_catalog"]
    list_display = ["name", "currency_catalog", "vat_catalog"]
    fields = (
        "name",
        # "supplier",
        "currency_catalog",
        "vat_catalog",
    )
    list_display_links = [
        "name",
    ]
    def get_readonly_fields(self, request, obj=None):
        if obj:
            
            return ["name",]
        else:
            return [
                "",
            ]

    def has_delete_permission(self, request, obj=None):
        return False
    


class CategoryProductInline(admin.TabularInline):

    model = CategoryProduct
    fields = ("name",)


class SupplierCategoryProductAllAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS
    form = SupplierCategoryProductAllAdminForm
    list_display = (
        "category_supplier",
        "group_supplier",
        "name",
        "supplier",
        "vendor",
        "article_name",
        "is_correct",
        "is_need",
        # "category_catalog",
        # "group_catalog",
    )
    list_display_links = [
        "name",
    ]
    fields = (
        "name",
        "supplier",
        "vendor",
        "article_name",
        "category_supplier",
        "group_supplier",
        "category_catalog",
        "group_catalog",
    )
    # list_editable = ("category_catalog", "group_catalog")
    readonly_fields = (
        "name",
        "supplier",
        "vendor",
        "article_name",
        "is_correct",
    )
    # search_fields = ('name', 'supplier',)
    list_filter = [
        "supplier",
        "vendor",
        "category_supplier",
        "group_supplier",
    ]

    class Media:
        css = {
            "all": ("supplier/css/admin_price.css",),
        }

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.autosave_tag == True:
                if obj.category_supplier != None and obj.group_supplier == None:
                    return [
                        "article_supplier",
                        "supplier",
                        "category_supplier",
                        "article_name",
                        "name",
                        "is_correct",
                    ]

                elif obj.category_supplier != None and obj.group_supplier != None:
                    return [
                        "article_supplier",
                        "supplier",
                        "category_supplier",
                        "group_supplier",
                        "article_name",
                        "name",
                        "is_correct",
                    ]
            else:
                [
            "is_correct",
        ]

            return ["article_supplier", "supplier", "article_name","is_correct",]
        return [
            "is_correct",
        ]

    def save_model(self, request, obj, form, change):
        if obj:
            pass
        else:
            obj.autosave_tag = False
        super().save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj):
        fields = super(SupplierCategoryProductAllAdmin, self).get_fieldsets(
            request, obj
        )
        fieldsets = [
            (
                None,
                {
                    "fields": [
                        "is_correct",
                        "is_need",
                        "name",
                        "supplier",
                        "vendor",
                        "article_name",
                        "category_supplier",
                        "group_supplier",
                        "category_catalog",
                        "group_catalog",
                    ]
                },
            )
        ]

        if obj and obj.supplier.slug == "iek":
            return fieldsets
        else:
            return fields

    def has_delete_permission(self, request, obj=None):
        return False


class SupplierCategoryProductAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS
    form = SupplierCategoryProductAdminForm
    list_filter = [
        "supplier",
        "vendor",
    ]

    list_display = (
        "name",
        "supplier",
        "vendor",
        "article_name",
        # "category_catalog",
    )
    fields = (
        "name",
        "supplier",
        "vendor",
        "article_name",
        "category_catalog",
        "group_catalog",
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.autosave_tag == True:
                return ["article_supplier", "supplier", "article_name", "name"]
            else:
                pass
            return ["article_supplier", "supplier", "article_name"]
        return [
            "",
        ]

    def save_model(self, request, obj, form, change):
        if obj:
            pass
        else:
            obj.autosave_tag = False
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False


class SupplierGroupProductAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS
    list_filter = [
        "supplier",
        "vendor",
        "category_supplier",
    ]
    form = SupplierGroupProductAdminForm
    list_display = (
        "category_supplier",
        "name",
        "supplier",
        "vendor",
        "article_name",
        # "category_catalog",
    )
    list_display_links = [
        "name",
    ]
    fields = (
        "supplier",
        "vendor",
        "category_supplier",
        "article_name",
        "name",
        "category_catalog",
        "group_catalog",
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.autosave_tag == True:
                if obj.category_supplier != None:
                    return [
                        "article_supplier",
                        "supplier",
                        "category_supplier",
                        "article_name",
                        "name",
                    ]

            else:
                pass

            return ["article_supplier", "supplier", "article_name"]
        return [
            "",
        ]

    def save_model(self, request, obj, form, change):
        if obj:
            pass
        else:
            obj.autosave_tag = False
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False

class SupplierPromoGroupeAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS
    list_filter = [
        "supplier",
        "vendor",
        
    ]
    
    list_display = (
        "name",
        "supplier",
        "vendor",
    )
    list_display_links = [
        "name",
    ]
    fields = (
        "supplier",
        "vendor",
        "name",
    )




    def has_delete_permission(self, request, obj=None):
        return False


class DiscountAdmin(admin.ModelAdmin):
    form = DiscountForm
    list_display = (
        "percent",
        "supplier",
        "vendor",
        "category_supplier",
        "group_supplier",
        "category_supplier_all",
        "promo_groupe",
        "is_tag_pre_sale",
        
        
    )
    fields = (
        
        "supplier",
        "vendor",
        "category_supplier",
        "group_supplier",
        "category_supplier_all",
        "promo_groupe",
        "percent",
        "is_tag_pre_sale",
    )

    def save_model(self, request, obj, form, change):
        if change:
            sale_old = Discount.objects.get(id=obj.id)
        super().save_model(request, obj, form, change)
        if change:

            if sale_old.is_tag_pre_sale != obj.is_tag_pre_sale:
                price = Price.objects.filter(sale=obj.id)

                def background_task():
                    # Долгосрочная фоновая задача
                    for price_one in price:
                        price_one._change_reason = "Автоматическое"
                        price_one.save()

                daemon_thread = threading.Thread(target=background_task)
                daemon_thread.setDaemon(True)
                daemon_thread.start()

        # super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        id_sec = obj.id
        obj.delete()
        price = Price.objects.filter(sale__isnull=True)

        # price = Price.objects.filter(sale=id_sec)
        def background_task():
            # Долгосрочная фоновая задача
            for price_one in price:
                price_one._change_reason = "Автоматическое"
                price_one.save()

        daemon_thread = threading.Thread(target=background_task)
        daemon_thread.setDaemon(True)
        daemon_thread.start()

    def delete_queryset(self, request, queryset):
        queryset.delete()
        price = Price.objects.filter(sale__isnull=True).order_by("-id")

        def background_task():
            # Долгосрочная фоновая задача
            for price_one in price:
                price_one._change_reason = "Автоматическое"
                price_one.save()
                # update_change_reason(price_one, "Автоматическое")

        daemon_thread = threading.Thread(target=background_task)
        daemon_thread.setDaemon(True)
        daemon_thread.start()


class VendorWebAdmin(admin.ModelAdmin):
    model = Vendor
    list_display = (
        "name",
        "is_view_index_web",
        "article",
    )
    fields = (
        "name",
        "name_web",
        "img",
        "is_view_index_web",
        "article",
        "article_filter",
    )
    readonly_fields = ["name"]

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Vendor, SupplierVendor)
admin.site.register(SupplierCategoryProductAll, SupplierCategoryProductAllAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(SupplierCategoryProduct, SupplierCategoryProductAdmin)
admin.site.register(SupplierGroupProduct, SupplierGroupProductAdmin)
admin.site.register(SupplierPromoGroupe, SupplierPromoGroupeAdmin)
website_admin.register(Vendor, VendorWebAdmin)
