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
    
    client = None
    if context.request.path_info == "/marking/":
        manager = AdminUser.objects.get(email="maksim.skitchenko@motrum.ru")
        phone_manager = get_phone_number(manager.phone)
        phone_manager = 88463004117
        if (
            context.request.user.is_authenticated
            and context.request.user.is_staff == False
        ):
            client = Client.objects.get(username=context.request.user)

        return {
            "roistat":True,
            "is_need": True,
            "user": client,
            "manager": manager,
            "phone_manager": phone_manager,
        }
    elif (
        context.request.path_info == "/robots/"
        or context.request.path_info == "/cobots-palett/"
        or context.request.path_info == "/cobots-box/"
        or context.request.path_info == "/cobots-packing/"
    ):
        manager = AdminUser.objects.get(email="sergey.govorkov@motrum.ru")
        phone_manager = get_phone_number(manager.phone)
        phone_manager = 88463004117
       
        if (
            context.request.user.is_authenticated
            and context.request.user.is_staff == False
        ):
            client = Client.objects.get(username=context.request.user)
        return {
            "roistat":True,
            "is_need": True,
            "user": client,
            "manager": manager,
            "phone_manager": phone_manager,
        }
    else:
        if (
            context.request.user.is_authenticated
            and context.request.user.is_staff == False
        ):
            try:
                client = Client.objects.get(username=context.request.user)
                manager = client.manager
                phone_manager = get_phone_number(manager.phone)

                return {
                    "roistat":False,
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
