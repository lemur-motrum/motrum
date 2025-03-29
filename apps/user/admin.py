from django import forms
from django.contrib.auth.models import Group
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from requests import request

from apps.core.bitrix_api import get_manager
from apps.user.forms import PasswordForm
from apps.user.models import AdminUser, CustomUser, ManagerWebUser, Roles
from project.admin import website_admin


class AdminUserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "email", "admin_type","is_active","bitrix_id","phone",)
    form = PasswordForm
    readonly_fields = ("bitrix_id",)
    fieldsets = (
        (
            "Персональная информация",
            {
                "fields": (
                    
                    "username",
                    "bitrix_id",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "email",
                    "admin_type",
                    "password",
                    "is_active",
                    "image",
                    "phone",
                )
            },
        ),
    )
    # def save_model(self, request, obj, form, change):
    #     # if obj.pk:
    #     #     get_manager()
    #     # else:
    #     #     get_manager()
        
    #     super().save_model(request, obj, form, change)
        
    # def has_delete_permission(self, request, obj=None):
    #     return False


class ClientAdminWeb(admin.ModelAdmin):
    pass
    # fields = ("contact_name", "email", "phone", )
    # list_display = [
    #     "phone",
    #     "contact_name",
    # ]


admin.site.register(AdminUser, AdminUserAdmin)

admin.site.unregister(Group)
