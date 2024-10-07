from django.contrib import admin
from django.contrib.auth.models import Group
from apps.client.models import AccountRequisites, Client, Requisites
from project.admin import website_admin
from django.template.loader import get_template

# Register your models here.


class RequisitesInlineWeb(admin.StackedInline):
    model = Requisites
    extra = 1
    # def has_add_permission(self, request):
    #     return False


class ClientAdminWeb(admin.ModelAdmin):

    fields = (
        "contact_name",
        "email",
        "phone",
    )
    list_display = [
        "phone",
        "contact_name",
    ]

    inlines = [
        RequisitesInlineWeb,
    ]
    # def has_add_permission(self, request):
    #     return False
    # def has_delete_permission(self, request,obj=None):
    #     return False


# class AccountRequisitesAdminInline(admin.TabularInline):
#     extra = 1
#     model = AccountRequisites

# class RequisitesAdmin(admin.ModelAdmin):
#     inlines = AccountRequisitesAdminInline,
#     fields = 'legal_entity','image_inline',
#     readonly_fields= 'image_inline',

#     def image_inline(self, *args, **kwargs):
#         context = getattr(self.response, 'context_data', None) or {} # somtimes context.copy() is better
#         inline = context['inline_admin_formset'] = context['inline_admin_formsets'].pop(0)
#         return get_template(inline.opts.template).render(context, self.request)

#     def render_change_form(self, request, *args, **kwargs):
#         self.request = request
#         self.response = super().render_change_form(request, *args, **kwargs)
#         return self.response

# class RequisitesInline(admin.StackedInline):
#     extra = 1
#     model = Requisites

#     readonly_fields = 'image_inline',


#     def image_inline(self, obj=None, *args, **kwargs):
#         context = getattr(self.modeladmin.response, 'context_data', None) or {}
#         admin_view = RequisitesAdmin(self.model, self.modeladmin.admin_site).add_view(self.modeladmin.request)
#         inline = admin_view.context_data['inline_admin_formsets'][0]
#         return get_template(inline.opts.template).render(context | {'inline_admin_formset': inline}, self.modeladmin.request)
#     def get_formset(self, *args, **kwargs):
#         formset = super().get_formset(*args, **kwargs)
#         formset.form.modeladmin = self.modeladmin
#         return formset


# class ClientAdminWeb(admin.ModelAdmin):
#     inlines = RequisitesInline,
#     fields = 'contact_name',

#     def render_change_form(self, request, *args, **kwargs):
#         self.request = request
#         response = self.response = super().render_change_form(request, *args, **kwargs)
#         return response

#     def get_inline_instances(self, *args, **kwargs):
#         yield from ((inline, vars(inline).update(modeladmin=self))[0] for inline in super().get_inline_instances(*args, **kwargs))


# website_admin.register(Client, ClientAdminWeb)
# website_admin.register(Requisites,RequisitesAdmin)
