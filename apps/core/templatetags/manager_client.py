from django import template

from apps.client.models import Client
from apps.user.models import AdminUser

register = template.Library()


def get_phone_number(numbers):
    numbers_lst = numbers.split("\n")
    only_digits = [
        "".join([c for c in element if c.isdigit()]) for element in numbers_lst
    ]
    formted_lst = [
        f"+{a} ({b}{c}{d}) {e}{f}{g}-{h}{i}-{j}{k}"
        for a, b, c, d, e, f, g, h, i, j, k in only_digits[:8]
    ]
    result = "\n".join(formted_lst)
    return result


@register.inclusion_tag("core/includes/manager.html", takes_context=True)
def manager_client(context):
    if context.request.user.is_authenticated and context.request.user.is_staff == False:
        try:
            client = Client.objects.get(username=context.request.user)
            manager = client.manager
            phone_manager = get_phone_number(manager.phone)

            return {
                "is_need": True,
                "user": context.request.user,
                "manager": manager,
                "phone_manager": phone_manager,
            }
        except Client.DoesNotExist:
            return {
                "is_need": False,
            }

    else:
        return {
            "is_need": False,
        }
