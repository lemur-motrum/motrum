import json
from django import template
from django.template import loader



from apps.notifications.models import Notification
from apps.product.models import ProductCart

register = template.Library()


@register.inclusion_tag("core/includes/lk_elem.html", takes_context=True)
def lk_link(context):
    # cookie = context.request.COOKIES.get("cart")
    current_user = context.request.user.id
    notifications = Notification.objects.filter(client_id = current_user,is_viewed=False ).order_by("order")
    count = notifications.count()
    
    return {
        "count": count,
    }
