from django import forms
from django.contrib.auth.models import Group
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from requests import request

from apps.user.forms import PasswordForm
from apps.user.models import AdminUser, CustomUser, ManagerWebUser, Roles
from project.admin import website_admin


class AdminUserAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name", "email", "admin_type")
    form = PasswordForm
    fieldsets = (
        (
            "Персональная информация",
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "admin_type",
                    "password",
                )
            },
        ),
    )


class ClientAdminWeb(admin.ModelAdmin):
    pass
    # fields = ("contact_name", "email", "phone", )
    # list_display = [
    #     "phone",
    #     "contact_name",
    # ]


admin.site.register(AdminUser, AdminUserAdmin)

admin.site.unregister(Group)
