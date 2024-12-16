from http.cookiejar import LoadError

from traceback import format_tb
from django.contrib import admin
from django.forms import Textarea
from django.utils.html import mark_safe

from apps.logs.models import LogsAddProduct,LogsError, LogsInfoError

# Register your models here.
class LogsErrorAdmin(admin.ModelAdmin):
    list_display_links = None
    list_display = [
        "date",
        "location",
        "info",
    ]
    
class LogsAddProductAdmin(admin.ModelAdmin):
    list_display_links = None
    list_display = [
        "date",
        "Ссылка",
        # "product",
        # "Ссылка",
        
    ] 
    class Media:
        css = {
            'all': ['logs/css/mymodel_list.css']
        }

        # css = {'all': ('logs/css/mymodel_list.css')}
    
    def Ссылка(self, obj):
        
        return mark_safe('<a href="/admin/product/product/{}/change/">{}</a>'.format(obj.product.id, obj.product.name)) 
 
class LogsInfoErrorAdmin(admin.ModelAdmin):
    list_display_links = None
    list_display = [
        "date",
        "location",
        "info",
    ]    
admin.site.register(LogsAddProduct,LogsAddProductAdmin)    
admin.site.register(LogsError,LogsErrorAdmin)
admin.site.register(LogsInfoError,LogsInfoErrorAdmin)