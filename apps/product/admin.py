from django.contrib import admin

from apps.product.models import CategoryProduct, GroupProduct, Lot

# Register your models here.
class GroupProductInline(admin.TabularInline):
    model = GroupProduct
    fields  = ('name',)

    
   
class SupplierAdmin(admin.ModelAdmin):
    fields  = ('name',)
    
    inlines = [
        GroupProductInline,
    ]
    
class GroupProductAdmin(admin.ModelAdmin):
    list_display   = ('name',)
    
class LotAdmin(admin.ModelAdmin):
    fields   = ('name','name_shorts',)
    

    
admin.site.register(CategoryProduct,SupplierAdmin)
admin.site.register(GroupProduct,GroupProductAdmin)
admin.site.register(Lot,LotAdmin)