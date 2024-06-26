from http.cookiejar import LoadError
from django.contrib import admin

from apps.logs.models import LogsProductChange,LogsError

# Register your models here.
# admin.site.register(LogsProductChange)
admin.site.register(LogsError)