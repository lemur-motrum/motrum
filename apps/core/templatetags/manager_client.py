from django import template

from apps.client.models import Client
from apps.user.models import AdminUser

register = template.Library()


def get_phone_number(numbers, roistat=False):
    numbers_lst = numbers.split("\n")
    only_digits = [
        "".join([c for c in element if c.isdigit()]) for element in numbers_lst
    ]
    if roistat != True:
        formted_lst = [
            f"8 ({b}{c}{d}) {e}{f}{g}-{h}{i}-{j}{k}"
            for a, b, c, d, e, f, g, h, i, j, k in only_digits[:8]
        ]
    else:
        formted_lst = [
            f"({b}{c}{d}) {e}{f}{g}-{h}{i}-{j}{k}"
            for a, b, c, d, e, f, g, h, i, j, k in only_digits[:8]
        ]
    result = "\n".join(formted_lst)
    return result


@register.inclusion_tag("core/includes/manager.html", takes_context=True)
def manager_client(context):

    client = None
    if context.request.path_info == "/marking/":
        manager = AdminUser.objects.get(email="maksim.skitchenko@motrum.ru")
        phone_manager = "78463004117"
        frontend_num = get_phone_number(phone_manager, True)

        if (
            context.request.user.is_authenticated
            and context.request.user.is_staff == False
        ):
            client = Client.objects.get(username=context.request.user)

        return {
            "roistat": True,
            "is_need": True,
            "user": client,
            "manager": manager,
            "phone_manager": phone_manager,
            "frontend_num": frontend_num,
        }
    elif (
        context.request.path_info == "/robots/"
        or context.request.path_info == "/cobots-palett/"
        or context.request.path_info == "/cobots-box/"
        or context.request.path_info == "/cobots-packing/"
    ):
        manager = AdminUser.objects.get(email="sergey.govorkov@motrum.ru")
        phone_manager = "78463004117"
        frontend_num = get_phone_number(phone_manager, True)

        if (
            context.request.user.is_authenticated
            and context.request.user.is_staff == False
        ):
            client = Client.objects.get(username=context.request.user)
        return {
            "roistat": True,
            "is_need": True,
            "user": client,
            "manager": manager,
            "phone_manager": phone_manager,
            "frontend_num": frontend_num,
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
                    "roistat": False,
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
