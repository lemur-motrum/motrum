from locale import currency
from django.contrib import admin

from apps.core.models import Currency, CurrencyPercent, Vat
from apps.product.admin import LotAdmin
from apps.product.models import Lot

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
         
            



# Register your models here.


admin.site.register(Currency)
admin.site.register(CurrencyPercent,CurrencyPercentAdmin)
admin.site.register(Vat)



