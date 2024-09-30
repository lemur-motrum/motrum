from django import template

import json

from apps.product.models import ProductCart
from apps.notifications.models import Notification

register = template.Library()


@register.inclusion_tag('core/header/header_cart_lk_items.html', takes_context=True)
def header_menu_counter(context):
    cookie_cart = context.request.COOKIES.get("cart")
    current_user = context.request.user.id
    notifications = Notification.objects.filter(client_id = current_user,is_viewed=False )
    notifications_order = notifications.filter(type_notification="STATUS_ORDERING")
    if cookie_cart:
        cart_id = json.loads(cookie_cart)
        cart = ProductCart.objects.filter(cart=cart_id)
        count_cart = len(cart)
    else:
        count_cart = 0
    print(count_cart)
    count_notifications_all = notifications.count() 
    count_notifications_order = notifications_order.count()    
    return {
        "count_cart": count_cart,
        "count_notifications_all": count_notifications_all,
        "notifications_order":count_notifications_order,
        "request":context.request,
        
    }
    
    # if context.request.user.is_authenticated:
    #     user = context.request.user.participant
    #     return {
    #         'user': user,
    #         'localtime': user.get_participant_time(),
    #         'view_name': context.request.resolver_match.view_name,
    #         'is_today_report': user.is_today_report(),
    #         'not_viewed_notifications_amount': Notification(participant=user).not_viewed_amount(),
    #     }
    # else:
        # return {
        #     'user': context.request.user,
        # }