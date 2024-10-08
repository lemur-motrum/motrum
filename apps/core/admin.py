from locale import currency
from django.contrib import admin

from apps.core.models import BaseInfo, BaseInfoAccountRequisites, Currency, CurrencyPercent, SliderMain, Vat
from apps.product.admin import LotAdmin
from apps.product.models import Lot
from project.admin import website_admin

class CurrencyPercentAdmin(admin.ModelAdmin):
    # model = CurrencyPercent
    # list_display = ("percent",)
    
    def has_add_permission(self, request,):
        currency = CurrencyPercent.objects.filter().exists()
        if currency == True:
            return False
        else:
            return True
        
    def has_delete_permission(self, request,obj=None):
        return False
    
class CurrencyAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request,obj=None):
        return False    
         
class VatAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request,obj=None):
        return False            


class BaseInfoAccountRequisitesInline(admin.TabularInline):
    model = BaseInfoAccountRequisites
    
class BaseInfoAdmin(admin.ModelAdmin):
    inlines = [
        BaseInfoAccountRequisitesInline,
    ]
    def has_delete_permission(self, request,obj=None):
        return False            





# АДМИНКА ДЛЯ ВЕБСАЙТА            
class SliderMainAdminWeb(admin.ModelAdmin):
    list_display = [
        "name",
        "type_slider",
        "active",
    ]
    def get_exclude(self, request, obj=None):
 
        if obj:
            if obj.product_promote:
                return ["video","slug"]
            else:
                return ["product_promote","slug"]
        else:
            return ["product_promote","slug"]
    def has_delete_permission(self, request,obj=None):
        return False
# Register your models here.

admin.site.register(BaseInfo, BaseInfoAdmin)
admin.site.register(Currency,CurrencyAdmin)
admin.site.register(CurrencyPercent,CurrencyPercentAdmin)
admin.site.register(Vat,VatAdmin)

website_admin.register(SliderMain,SliderMainAdminWeb)



