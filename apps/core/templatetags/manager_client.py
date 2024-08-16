from django import template

from apps.client.models import Client
from apps.user.models import AdminUser

register = template.Library()


@register.inclusion_tag("core/includes/manager.html", takes_context=True)
def manager_client(context):
    if context.request.user.is_authenticated and context.request.user.is_staff == False:
        try:
            client = Client.objects.get(username=context.request.user)
            manager = client.manager
            return {
                "is_need": True,
                "user": context.request.user,
                "manager": manager,
            }
        except Client.DoesNotExist:
            return {
                "is_need": False,
            }

    else:
        return {
            "is_need": False,
        }
