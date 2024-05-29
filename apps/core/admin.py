from django.contrib import admin

from apps.core.models import Currency, CurrencyPercent, Vat




# Register your models here.


admin.site.register(Currency)
admin.site.register(Vat)
admin.site.register(CurrencyPercent)

