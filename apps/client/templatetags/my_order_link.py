import json
from django import template
from django.template import loader



from apps.notifications.models import Notification
from apps.product.models import ProductCart

register = template.Library()


@register.inclusion_tag("client/includes/my_order_elem.html", takes_context=True)
def my_order_link(context):
    # cookie = context.request.COOKIES.get("cart")
    current_user = context.request.user.id
    notifications = Notification.objects.filter(client_id = current_user,type_notification="STATUS_ORDERING",is_viewed=False, )
    count = notifications.count()
    return {
        "count": count,
    }