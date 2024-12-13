from ast import Try
import os
import random
import traceback
from django.conf import settings
from fast_bitrix24 import Bitrix
from django.http import HttpResponseRedirect
from requests import Response

from apps.client.api.serializers import OrderSerializer
from apps.client.models import STATUS_ORDER_BITRIX, Order
from apps.core.utils import client_info_bitrix, create_info_request_order_bitrix
from apps.logs.utils import error_alert
from apps.product.models import Cart
from apps.specification.models import ProductSpecification
from apps.user.models import AdminUser


# проверка и получение основной инфы для создания заказа
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
            return (next_url, context, True)
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
                    return (next_url, response, False)
                else:
                    next_url = "/admin_specification/error-b24/"
                    context = {
                        "error": "Неприведенная ошибка во время создания заказа. Повторите. "
                    }
                    return (next_url, response, True)

    else:
        next_url = "/admin_specification/error-b24/"
        error_text = ""
        if data_admin["status_admin"] == 401:
            error_text = "Неверные данные для логина. Токен не совпадает с почтой или этого юзера нет в системе окт"
        elif data_admin["status_admin"] == 403:
            error_text = "Нет прав доступа к системе"

        context = {"error": error_text}
        return (next_url, context, True)


# проверка полей на заполненность при создании заказа-возврат текста для ошибки
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


# получение статусов для актуальных заказов
def get_status_order():
    try:

        def get_status_bx(status):
            for choice in STATUS_ORDER_BITRIX:
                if choice[1] == status:
                    return choice[0]

        not_view_status = ["COMPLETED", "CANCELED"]
        actual_order = Order.objects.exclude(
            status__in=not_view_status, id_bitrix__isnull=True
        ).values("id_bitrix")

        webhook = settings.BITRIX_WEBHOOK

        bx = Bitrix("https://b24-j6zvwj.bitrix24.ru/rest/1/qgz6gtuu9qqpyol1/")
        orders = [d["id_bitrix"] for d in actual_order]
        orders = [2]

        orders_bx = bx.get_by_ID("crm.deal.get", orders)

        if len(orders) == 1:
            orders_bx = {orders_bx["ID"]: orders_bx}

        for order_bx in orders_bx.values():

            print(order_bx)
            id_bx = order_bx["ID"]

            status_bx = order_bx["STAGE_ID"]
            print(id_bx, status_bx)
            order = Order.objects.filter(id_bitrix=id_bx).last()
            if order:
                status = get_status_bx(status_bx)
                if status == "SHIPMENT_":
                    if order.type_delivery == "Самовывоз":
                        status = "SHIPMENT_PICKUP"
                    else:
                        status = "SHIPMENT_AUTO"
                print(status)
                order.status = status
                order.save()

    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        error = "file_api_error"
        location = "Получение статусов битрикс24"
        info = f"Получение статусов битрикс24. Тип ошибки:{e}{tr}"
        e = error_alert(error, location, info)

# сохранение всех данных по заказу:
def add_info_order(request, order,type_save):
    
    webhook = settings.BITRIX_WEBHOOK
    bx = Bitrix("https://b24-j6zvwj.bitrix24.ru/rest/1/qgz6gtuu9qqpyol1/")
    # pdf = request.build_absolute_uri(order.bill_file_no_signature.url)
    # pdf_signed = request.build_absolute_uri(order.bill_file.url)
    # if order.specification.file:
    #     document_specification = request.build_absolute_uri(
    #         order.specification.file.url
    #     )
    # else:
    #     document_specification = None

    # ТОВАРЫ СДЕЛКИ
    is_order_pros_bx = save_product_order_bx(bx,order)

    
    if is_order_pros_bx:
        return True
    else:
        return False
    

# add_info_order сохранение товаров  в заказ битрикс
def save_product_order_bx(bx,order):
    order_products = ProductSpecification.objects.filter(
        specification=order.specification
    )

    order_products_data = []
    for order_products_i in order_products:
        order_info = {
            "ID": "28",
            "PRODUCT_NAME": order_products_i.product.name,
            "PRICE": 3000,
            "QUANTITY": order_products_i.quantity,
            # "PRODUCT_DESCRIPTION":order_products_i.product.article,
            "PRODUCT_NAME": order_products_i.product.name,
        }
        order_products_data.append(order_info)
    data_bx_product = {
        "id": order.id_bitrix,
        "rows": order_products_data,
    }


    # product_bx = bx.call("crm.deal.productrows.set", data_bx_product)
    # print(product_bx)
    # product_bx = bx.get_all("crm.item.productrow.fields",)
    # product_bx = bx.call(
    #     "crm.item.productrow.update",
    #     {
    #         "id": 30,
    #         "fields": {
    #             "price": "1",
    #         }
    #     },
    # )
    # print(product_bx)
    
    # product_bx = bx.call("crm.item.get", data_bx_product)
    # product_bx_get = bx.call("crm.deal.productrows.get", data_bx_product)
    # print(product_bx_get)
    
    return False

# сохранение информации по товарам после 1с 
def save_product_info_bx():
    webhook = settings.BITRIX_WEBHOOK
    bx = Bitrix("https://b24-j6zvwj.bitrix24.ru/rest/1/qgz6gtuu9qqpyol1/")

# новые документы после появления точных сроков поставки
def save_new_doc_bx(pdf,pdf_signed):
    webhook = settings.BITRIX_WEBHOOK
    bx = Bitrix("https://b24-j6zvwj.bitrix24.ru/rest/1/qgz6gtuu9qqpyol1/")


def save_params_product_bx(data):
    webhook = settings.BITRIX_WEBHOOK
    bx = Bitrix("https://b24-j6zvwj.bitrix24.ru/rest/1/qgz6gtuu9qqpyol1/")
    
    return True

def save_payment_order_bx(data):
    webhook = settings.BITRIX_WEBHOOK
    bx = Bitrix("https://b24-j6zvwj.bitrix24.ru/rest/1/qgz6gtuu9qqpyol1/")
    
    return True

def save_shipment_order_bx(data):
    webhook = settings.BITRIX_WEBHOOK
    bx = Bitrix("https://b24-j6zvwj.bitrix24.ru/rest/1/qgz6gtuu9qqpyol1/")
    
    return True