from dataclasses import field
from django.contrib import admin

from apps.product.admin import GroupProductInline
from apps.product.models import CategoryProduct, GroupProduct

# Register your models here.
from .models import (
    Discount,
    Supplier,
    SupplierCategoryProduct,
    SupplierCategoryProductAll,
    SupplierGroupProduct,
    Vendor,
)


class VendorInline(admin.TabularInline):
    model = Vendor
    fields = (
        "name",
        "currency_catalog",
        "vat_catalog",
    )


class SupplierAdmin(admin.ModelAdmin):
    fields = ("name",)

    inlines = [
        VendorInline,
    ]


class SupplierVendor(admin.ModelAdmin):
    fields = (
        "name",
        "supplier",
        "currency_catalog",
        "vat_catalog",
    )


# class CategoryProductInline(admin.TabularInline):
#     model = CategoryProduct
#     fields = ("name",)


class SupplierCategoryProductAllAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "supplier",
        "vendor",
        "article_name",
        "category_supplier",
        "group_supplier",
        "category_catalog",
        "group_catalog",
    )
    fields = (
        "name",
        "supplier",
        "vendor",
        "article_name",
        "category_catalog",
        "group_catalog",
    )
    list_editable = ("category_catalog", "group_catalog")
    readonly_fields = (
        "name",
        "supplier",
        "vendor",
        "article_name",
    )
    # search_fields = ('name', 'supplier',)
    list_filter = [
        "supplier",
    ]
    # inlines = [
    #     GroupProductInline,
    # ]

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "group_catalog":
    #         kwargs["queryset"] = GroupProduct.objects.filter(category=request.)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


# class SupplierCategoryProduct(admin.ModelAdmin):
#     list_display = (
#         "name",
#         "supplier",
#         "vendor",
#         "article_name",
#         "category_catalog",
#     )
#     fields = (
#         "name",
#         "supplier",
#          "vendor",
#         "article_name",
#         "category_catalog",
#         "group_catalog"
#     )
#     list_editable = (

#         "category_catalog",
#         "group_catalog"
#     )
#     readonly_fields = ('name', 'supplier', "vendor", "article_name",)
#     # search_fields = ('name', 'supplier',)
#     list_filter = ['supplier',]
#     # inlines = [
#     #     GroupProductInline,
#     # ]

#     # def formfield_for_foreignkey(self, db_field, request, **kwargs):
#     #     if db_field.name == "group_catalog":
#     #         kwargs["queryset"] = GroupProduct.objects.filter(category=request.)
#     #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


class DiscountAdmin(admin.ModelAdmin):

    list_display = (
        "supplier",
        "vendor",
        "category_supplier",
        "group_supplier",
        "category_supplier_all",
        "percent",
      
    )
    fields = (
        "supplier",
        "vendor",
        "category_supplier",
        "group_supplier",
        "category_supplier_all",
        "percent",
       
    )


admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Vendor, SupplierVendor)
admin.site.register(SupplierCategoryProductAll, SupplierCategoryProductAllAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(SupplierCategoryProduct)
admin.site.register(SupplierGroupProduct)
