from django.contrib import admin

# Register your models here.
from .models import Supplier, Vendor

class VendorInline(admin.TabularInline):
    model = Vendor
    fields  = ('name','currency_catalog',)

    
    
class SupplierAdmin(admin.ModelAdmin):
    fields  = ('name',)
    
    inlines = [
        VendorInline,
    ]
    
class SupplierVendor(admin.ModelAdmin):
    fields  = ('name','currency_catalog',)
    

admin.site.register(Supplier,SupplierAdmin)
admin.site.register(Vendor,SupplierVendor)
