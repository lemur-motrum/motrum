from dataclasses import field
from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from simple_history.utils import update_change_reason

from apps.product.admin import GroupProductInline
from apps.product.models import CategoryProduct, GroupProduct, Price
from apps.supplier.forms import DiscountForm

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
    list_display = ["supplier","name","currency_catalog","vat_catalog" ]
    fields = (
        "name",
        "supplier",
        "currency_catalog",
        "vat_catalog",
    )
    list_display_links = ["name",]



class CategoryProductInline(admin.TabularInline):
    model = CategoryProduct
    fields = ("name",)


class SupplierCategoryProductAllAdmin(admin.ModelAdmin):
    show_facets = admin.ShowFacets.ALWAYS
    list_display = (
        "category_supplier",
        "group_supplier",
        "name",
        "supplier",
        "vendor",
        "article_name",
       
        # "category_catalog",
        # "group_catalog",
    )
    list_display_links = ["name",]
    fields = (
        "name",
        "supplier",
        "vendor",
        "article_name",
        "category_supplier",
        "group_supplier",
        # "category_catalog",
        # "group_catalog",
    )
    # list_editable = ("category_catalog", "group_catalog")
    readonly_fields = (
        "name",
        "supplier",
        "vendor",
        "article_name",
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
            "all": ("supplier/css/my_styles.css",),
        }
    
    # def get_form(self, request, obj=None, **kwargs):
    #     form = super(SupplierCategoryProductAllAdmin, self).get_form(request, obj, **kwargs)
    #     form.base_fields['group_supplier'].widget.attrs['style'] = 'width: 45px;'
    #     return form
    
    # def formfield_for_dbfield(self, db_field, **kwargs):
    #     field = super(SupplierCategoryProductAllAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    #     if db_field.name == 'group_supplier':
    #         field.widget.attrs['class'] = 'someclass ' + field.widget.attrs.get('class', '')
    #     return field
    
    # def formfield_for_dbfield(self, db_field, request, **kwargs):
       
    #     field = super().formfield_for_dbfield(db_field, request, **kwargs)
    #     if db_field.name == 'group_supplier':
    #         field.widget.attrs['style'] =  'word-wrap: break-word'
    #         # field.widget.required = False
    #     return field
    
    
#     formfield_overrides = {
#         models.CharField: {'widget': TextInput(attrs={'size': '20'})},
      
#         models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40, 'style': 'white-space: normal;'})},
# }       
    # formfield_overrides = {
    #     models.CharField: {'widget': TextInput(attrs={'size':'20'})},
    #     models.TextField: {'widget': Textarea(attrs={'rows':2, 'cols':20})},
    # }
    # inlines = [
    #     GroupProductInline,
    # ]

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "group_catalog":
    #         kwargs["queryset"] = GroupProduct.objects.filter(category=request.)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SupplierCategoryProductAdmin(admin.ModelAdmin):
    
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
        # "category_catalog",
        # "group_catalog"
    )
    
    # list_editable = (

    #     "category_catalog",
    #     "group_catalog"
    # )
    # readonly_fields = ('name', 'supplier', "vendor", "article_name",)
    # # search_fields = ('name', 'supplier',)
    # list_filter = ['supplier',]
    # inlines = [
    #     GroupProductInline,
    # ]

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "group_catalog":
    #         kwargs["queryset"] = GroupProduct.objects.filter(category=request.)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SupplierGroupProductAdmin(admin.ModelAdmin):
    list_display = (
        "category_supplier",
        "name",
        "supplier",
        "vendor",
        "article_name",
        
        # "category_catalog",
    )
    list_display_links = ["name",]
    fields = (
        "name",
        "supplier",
         "vendor",
        "article_name",
        "category_supplier",
        # "category_catalog",
        # "group_catalog"
    )
class DiscountAdmin(admin.ModelAdmin):
    form = DiscountForm
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
    
    def delete_model(self, request, obj):
        id_sec = obj.id
        obj.delete()
        price = Price.objects.filter(sale__isnull=True)
        for price_one in price:
            price_one.save()
            update_change_reason(price_one, "Автоматическое")
 
    def delete_queryset(self, request, queryset):
        queryset.delete()
        price = Price.objects.filter(sale__isnull=True)
        for price_one in price:
            price_one.save()
            update_change_reason(price_one, "Автоматическое")
        


admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Vendor, SupplierVendor)
admin.site.register(SupplierCategoryProductAll, SupplierCategoryProductAllAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(SupplierCategoryProduct,SupplierCategoryProductAdmin)
admin.site.register(SupplierGroupProduct,SupplierGroupProductAdmin)
