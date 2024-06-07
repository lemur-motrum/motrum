from django import forms
from django.contrib.auth.models import Group
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from requests import request

from apps.user.forms import PasswordForm
from apps.user.models import AdminUser, CustomUser, Roles




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
    # def save_model(self, request, obj, form, change):
    #     print(obj.password)
        
    #     if change:
    #        super().save_model(request, obj, form, change) 
    #     else:    
    #         if obj.password == "":
    #             form = PasswordForm
    #             raise forms.ValidationError(
    #             "Введите пароль"
    #         )
    #         else:
    #             super().save_model(request, obj, form, change)
                
            
       


    # def formfield_for_dbfield(self, db_field, request, **kwargs):
     
    #     # self.fields['password'].queryset = UserModel.objects.filter(id=request.usermodel.id)
    #     field = super().formfield_for_dbfield(db_field, request, **kwargs)
    #     if db_field.name == 'password':
    #         field.widget = forms.PasswordInput()
    #         field.widget.required = False
    #     return field
    
   

admin.site.register(AdminUser, AdminUserAdmin)
# admin.site.register(CustomUser, UserAdmin)
admin.site.unregister(Group)
# admin.site.register(Roles)
