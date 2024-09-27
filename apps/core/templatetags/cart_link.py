import json
from django import template
from django.template import loader


from apps.product.models import ProductCart

register = template.Library()


@register.inclusion_tag("core/includes/cart_elem.html", takes_context=True)
def cart_link(context):
    cookie = context.request.COOKIES.get("cart")
    
    if cookie:
        
        cart_id = json.loads(cookie)
        cart = ProductCart.objects.filter(cart=cart_id)
        count = len(cart)

    else:
        count = 0
    return {
        "count": count,
    }
