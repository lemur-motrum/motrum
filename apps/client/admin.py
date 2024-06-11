from django.contrib import admin

# Register your models here.
from .models import Client, Text1, Text2
from simple_history.admin import SimpleHistoryAdmin
admin.site.register(Client)


admin.site.register(Text1, SimpleHistoryAdmin)
admin.site.register(Text2, SimpleHistoryAdmin)