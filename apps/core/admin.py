from django.contrib import admin

from apps.core.models import Currency, CurrencyPercent, Vat
from apps.product.admin import LotAdmin
from apps.product.models import Lot




# Register your models here.


admin.site.register(Currency)
admin.site.register(CurrencyPercent)
admin.site.register(Vat)



