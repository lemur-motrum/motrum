import random

from django.http import HttpResponseRedirect
from requests import Response

from apps.client.api.serializers import OrderSerializer
from apps.client.models import Order
from apps.core.utils import client_info_bitrix
from apps.product.models import Cart
from apps.user.models import AdminUser


def order_bitrix(data, request):

    next_url = "/admin_specification/current_specification/"

    result = "ok"
    order_info = data["order"]
    company_info = data["company"]
    type_save = data["type_save"]
    print(company_info)
    data_admin = AdminUser.login_bitrix(data["login"], None, request)
    if data_admin["status_admin"] == 200:
        error_company, error_order = order_info_check(company_info, order_info)
        if error_company or error_order:
            next_url = "/admin_specification/error-b24/"
            error_text = "Не заполнены поля: "
            error_text += ", ".join(error_company)
            if error_order:
                error_text += ", "
                error_text += ", ".join(error_order)

            context = {"error": error_text}
            return (next_url, context,True)
        else:

            client_req, acc_req = client_info_bitrix(company_info)
            manager = AdminUser.objects.get(email=data["order"]["manager"])

            data_order = {
                "id_bitrix": order_info["id_bitrix"],
                "name": 123131,
                "requisites": client_req.id,
                "account_requisites": acc_req.id,
                "status": "",
                # "cart": cart.id,
                "prepay_persent": client_req.prepay_persent,
                "postpay_persent": client_req.postpay_persent,
                "manager": manager,
            }
            serializer_class = OrderSerializer
            try:
                order = Order.objects.get(id_bitrix=order_info["id_bitrix"])
                cart = order.cart
                data_order["cart"] = cart.id
                serializer = serializer_class(order, data=data_order, many=False)
            except Order.DoesNotExist:
                cart = Cart.create_cart_admin(None, data_admin["admin"])
                data_order["cart"] = cart.id
                serializer = serializer_class(data=data_order, many=False)

            finally:

                if serializer.is_valid():
                    serializer._change_reason = "Ручное"
                    order = serializer.save()
                    response = HttpResponseRedirect(next_url)

                    response.set_cookie("client_id", max_age=-1)
                    response.set_cookie("cart", cart.id, max_age=1000)
                    response.set_cookie("specificationId", max_age=-1)
                    response.set_cookie("type_save", type_save, max_age=1000)
                    return (next_url, response,False)
                else:
                    next_url = "/admin_specification/error-b24/"
                    context = {"error": "Неприведенная ошибка во время создания заказа. Повторите. "}
                    return (next_url, response,True)

    else:
        next_url = "/admin_specification/error-b24/"
        error_text = ""
        if data_admin["status_admin"] == 401:
            error_text = "Неверные данные для логина. Токен не совпадает с почтой или этого юзера нет в системе окт"
        elif data_admin["status_admin"] == 403:
            error_text = "Нет прав доступа к системе"

        context = {"error": error_text}
        return (next_url, context,True)


def order_info_check(company_info, order_info):
    not_info = []
    if company_info["id_bitrix"] == "":
        not_info.append("Битрикс номер компании")

    if company_info["legal_entity"] == "":
        not_info.append("Юридическое название клиента")

    if company_info["inn"] == "":
        not_info.append("ИНН")

    if company_info["kpp"] == "":
        not_info.append("kpp")

    if company_info["legal_post_code"] == "":
        not_info.append("Юридический адрес : индекс")

    if company_info["legal_city"] == "":
        not_info.append("Юридический адрес : город")

    if company_info["legal_address"] == "":
        not_info.append("Юридический адрес : адрес")

    if company_info["postal_post_code"] == "":
        not_info.append("Почтовый адрес : индекс")

    if company_info["postal_city"] == "":
        not_info.append("Почтовый адрес : город")

    if company_info["postal_address"] == "":
        not_info.append("Почтовый адрес : адрес")

    if company_info["tel"] == "":
        not_info.append("Телефон")

    if company_info["account_requisites"] == "":
        not_info.append("Расчётный счёт")

    if company_info["bank"] == "":
        not_info.append("Банк реквизитов")

    if company_info["ks"] == "":
        not_info.append("Корреспондентский счет (к/с)")

    if company_info["bic"] == "":
        not_info.append("БИК")

    not_info_order = []

    if order_info["id_bitrix"] == "":
        not_info.append("Битрикс номер сделки")

    if order_info["manager"] == "":
        not_info.append("Менеджер сделки")

    if order_info["satatus"] == "":
        not_info.append("Статус сделки")
    return (not_info, not_info_order)
