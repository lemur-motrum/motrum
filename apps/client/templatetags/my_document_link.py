import json
from django import template
from django.template import loader



from apps.notifications.models import Notification
from apps.product.models import ProductCart

register = template.Library()


@register.inclusion_tag("client/includes/my_document_elem.html", takes_context=True)
def my_document_link(context):
    # cookie = context.request.COOKIES.get("cart")
    current_user = context.request.user.id
    notifications = Notification.objects.filter(client_id = current_user,is_viewed=False, ).exclude(type_notification="STATUS_ORDERING")
    count = notifications.count()
    
    return {
        "count": count,
    }