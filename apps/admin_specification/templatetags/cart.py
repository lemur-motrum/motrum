import json
from django import template
from django.template import loader


from apps.product.models import ProductCart

register = template.Library()


@register.inclusion_tag("admin_specification/include/cart.html", takes_context=True)
def cart(context):
    cookie = context.request.COOKIES.get("cart")
    print(f"fasafasdfasfasfsaf {cookie}")
    if cookie:
        cart_id = json.loads(cookie)
        cart = ProductCart.objects.filter(cart=cart_id)
        print(cart)
        count = len(cart)

    else:
        count = 0
    return {
        "count": count,
    }
