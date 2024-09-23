import json
from django import template
from django.template import loader



from apps.notifications.models import Notification
from apps.product.models import ProductCart

register = template.Library()


@register.inclusion_tag("core/includes/orders_elem.html", takes_context=True)
def order_link(context):
    # cookie = context.request.COOKIES.get("cart")
    current_user = context.request.user.id
    notifications = Notification.objects.filter(client_id = current_user,type_notification="STATUS_ORDERING",is_viewed=False ).order_by("order").distinct('order')
    count = notifications.count()
    
    return {
        "count": count,
    }
