from http.cookiejar import LoadError
from traceback import format_tb
from django.contrib import admin
from django.forms import Textarea
from django.utils.html import mark_safe

from apps.logs.models import LogsAddProduct, LogsProductChange,LogsError

# Register your models here.
class LogsErrorAdmin(admin.ModelAdmin):
    
    list_display = [
        "date",
        "location",
        "info",
    ]
    
class LogsAddProductAdmin(admin.ModelAdmin):
    
    list_display = [
        "date",
        "product",
        "Ссылка",
        
    ] 
    class Media:
        css = {
            'all': ['logs/css/mymodel_list.css']
        }

        # css = {'all': ('logs/css/mymodel_list.css')}
    
    def Ссылка(self, obj):
        
        return mark_safe('<a href="/admin/product/product/{}/change/">Ссылка</a>'.format(obj.product.id)) 
    
admin.site.register(LogsAddProduct,LogsAddProductAdmin)    
admin.site.register(LogsError,LogsErrorAdmin)