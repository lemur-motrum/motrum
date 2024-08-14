from http.cookiejar import LoadError
from django.contrib import admin

from apps.logs.models import LogsProductChange,LogsError

# Register your models here.
class LogsErrorAdmin(admin.ModelAdmin):
    
    list_display = [
        "date",
        "location",
        "info",
    ]
admin.site.register(LogsError,LogsErrorAdmin)