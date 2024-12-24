import base64
import datetime
import os
import random
import traceback
from django.conf import settings
from fast_bitrix24 import Bitrix
from django.http import HttpResponseRedirect
from requests import Response

from apps.client.api.serializers import OrderSerializer
from apps.client.models import STATUS_ORDER_BITRIX, Order
from apps.core.models import Currency
from apps.core.utils import client_info_bitrix, create_info_request_order_bitrix
from apps.logs.utils import error_alert
from apps.product.models import Cart, CurrencyRate, Price, Product
from apps.specification.models import ProductSpecification
from apps.user.models import AdminUser
from project.settings import MEDIA_ROOT


def get_info_for_order_bitrix(bs_id_order, request):
    try:
        print("get_info_for_order_bitrix")
        webhook = settings.BITRIX_WEBHOOK
        webhook = "https://b24-760o6o.bitrix24.ru/rest/1/ernjnxtviludc4qp/"
        print(webhook)
        bx = Bitrix(webhook)
        # ПОЛУЧЕНИЕ ДАННЫХ СДЕЛКИ
        # orders_bx = bx.get_all("crm.deal.list")
        orders_bx = bx.get_by_ID("crm.deal.get", [bs_id_order])
        print("orders_bx", orders_bx)
        company = orders_bx["COMPANY_ID"]
        if company == "0":
            error_text = "К сделке не прикреплен клиент"
            next_url = "/admin_specification/error-b24/"
            context = {"error": error_text}
            return (next_url, context, True)
        else:# ПОЛУЧЕНИЕ ДАННЫХ ПОКУПАТЕЛЯ 
            data = {
                "company": {
                    "id_bitrix": 69,
                    # "manager": - битрикс ид менеджера
                    "legal_entity_motrum": 'ООО ПНМ "Мотрум"',
                    # "contract": "",
                    # "contract_date": "",
                    "contract": "07-06/25",
                    "contract_date": "2024-04-24",
                    # "legal_entity": '',
                    "legal_entity": 'ООО "АЛСТАР СЕРВИС"',
                    "inn": "1650236125",
                    "kpp": "88888888",
                    "ogrn": "",
                    # "legal_post_code": "",
                    "legal_post_code": "423800",
                    "legal_city": "Республика Татарстан, г. Набережные Челны",
                    "legal_address": "ул. Профильная, дом 53",
                    "postal_post_code": "443099",
                    "postal_city": "Республика Татарстан, г. Набережные Челны",
                    "postal_address": "ул. Профильная, дом 55",
                    "tel": "89276892277",
                    "account_requisites": "40702810762030005449",
                    "bank": 'ОТДЕЛЕНИЕ "БАНК ТАТАРСТАН" N8610 ПАО СБЕРБАНК',
                    "ks": "30101810600000000603",
                    "bic": "049205603",
                },
                "order": {
                    "id_bitrix": bs_id_order,
                    "manager": "ruslan.ovcharov1111@motrum.ru",
                    "status": "PROCESSING",
                    # "status": orders_bx["STAGE_ID"],
                },
            }
            company_bx = bx.get_by_ID("crm.company.get", [company])

            #    data["company"]['id_bitrix'] = company_bx['ID']
            #    data["company"]['legal_entity'] = company_bx['TITLE']
            error_company, error_order = order_info_check(data["company"], data["order"])
            print(error_company, error_order)
            # ошибка в покупателе
            if error_company or error_order:
                next_url = "/admin_specification/error-b24/"
                error_text = "Не заполнены поля клиента: "
                error_text += ", ".join(error_company)
                if error_order:
                    error_text += ", "
                    error_text += ", ".join(error_order)

                context = {"error": error_text}
                return (next_url, context, True)
            # все данные есть 
            else: 
                client_req, acc_req = client_info_bitrix(data['company'])
                # manager = AdminUser.objects.get(email=data["order"]["manager"])
                manager = AdminUser.objects.get(user=request.user)
                data_order = {
                    "id_bitrix": bs_id_order,
                    "name": 123131,
                    "requisites": client_req.id,
                    "account_requisites": acc_req.id,
                    "status":  data['order']['status'],
                    "prepay_persent": client_req.prepay_persent,
                    "postpay_persent": client_req.postpay_persent,
                    # "manager": manager,
                }
                serializer_class = OrderSerializer
                try:
                    order = Order.objects.get(id_bitrix=bs_id_order)
                    cart = order.cart
                    data_order["cart"] = cart.id
                    serializer = serializer_class(order, data=data_order, many=False)
                    next_url = "admin_specification/bx_start.html"
                    context = {
                            "type_save": "old",
                            "cart":cart.id,
                            "order":order.id,
                            
                            "serializer" : data_order,
                        }
                    if order.specification:
                        context['spes'] = order.specification.id,
                    else:
                        context['spes'] = None,
                    return (next_url, context, False)
                except Order.DoesNotExist:
                    data['order']['manager'] = manager
                    cart = Cart.create_cart_admin(None, manager)
                    data_order["cart"] = cart.id
                    serializer = serializer_class(data=data_order, many=False)
                    
                    if serializer.is_valid():
                        next_url = "/admin_specification/current_specification/"
                        serializer._change_reason = "Ручное"
                        order = serializer.save()
                        context = {
                            "type_save": "new",
                            "cart":cart.id,
                            "order":order.id,
                            "spes":None,
                            "serializer" : None,
                        }
                        return (next_url, context, False)
                    else:
                        next_url = "/admin_specification/error-b24/"
                        context = {
                            "error": "Неприведенная ошибка во время создания заказа. Презагрузите страницу. "
                        }
                        return (next_url, context, True)
    except Exception as e:
        tr = traceback.format_exc()
        error = "error"
        location = "первичное открытие сделки битрикс"
        info = f" ошибка {e}{tr}"
        e = error_alert(error, location, info)      


# проверка и получение основной инфы для создания заказа


def order_bitrix(data, request):
    pass

    # next_url = "/admin_specification/current_specification/"

    # result = "ok"
    # order_info = data["order"]
    # company_info = data["company"]
    # type_save = data["type_save"]
    # print(company_info)
    # data_admin = AdminUser.login_bitrix(data["login"], None, request)
    # if data_admin["status_admin"] == 200:
    #     error_company, error_order = order_info_check(company_info, order_info)
    #     if error_company or error_order:
    #         next_url = "/admin_specification/error-b24/"
    #         error_text = "Не заполнены поля: "
    #         error_text += ", ".join(error_company)
    #         if error_order:
    #             error_text += ", "
    #             error_text += ", ".join(error_order)

    #         context = {"error": error_text}
    #         return (next_url, context, True)
    #     else:

    #         client_req, acc_req = client_info_bitrix(company_info)
    #         manager = AdminUser.objects.get(email=data["order"]["manager"])

    #         data_order = {
    #             "id_bitrix": order_info["id_bitrix"],
    #             "name": 123131,
    #             "requisites": client_req.id,
    #             "account_requisites": acc_req.id,
    #             "status": "",
    #             # "cart": cart.id,
    #             "prepay_persent": client_req.prepay_persent,
    #             "postpay_persent": client_req.postpay_persent,
    #             "manager": manager,
    #         }
    #         serializer_class = OrderSerializer
    #         try:
    #             order = Order.objects.get(id_bitrix=order_info["id_bitrix"])
    #             cart = order.cart
    #             data_order["cart"] = cart.id
    #             serializer = serializer_class(order, data=data_order, many=False)
    #         except Order.DoesNotExist:
    #             cart = Cart.create_cart_admin(None, data_admin["admin"])
    #             data_order["cart"] = cart.id
    #             serializer = serializer_class(data=data_order, many=False)

    #         finally:

    #             if serializer.is_valid():
    #                 serializer._change_reason = "Ручное"
    #                 order = serializer.save()
    #                 response = HttpResponseRedirect(next_url)

    #                 response.set_cookie("client_id", max_age=-1)
    #                 response.set_cookie("cart", cart.id, max_age=1000)
    #                 response.set_cookie("specificationId", max_age=-1)
    #                 response.set_cookie("type_save", type_save, max_age=1000)
    #                 return (next_url, response, False)
    #             else:
    #                 next_url = "/admin_specification/error-b24/"
    #                 context = {
    #                     "error": "Неприведенная ошибка во время создания заказа. Повторите. "
    #                 }
    #                 return (next_url, response, True)

    # else:
    #     next_url = "/admin_specification/error-b24/"
    #     error_text = ""
    #     if data_admin["status_admin"] == 401:
    #         error_text = "Неверные данные для логина. Токен не совпадает с почтой или этого юзера нет в системе окт"
    #     elif data_admin["status_admin"] == 403:
    #         error_text = "Нет прав доступа к системе"

    #     context = {"error": error_text}
    #     return (next_url, context, True)


# проверка полей на заполненность при создании заказа-возврат текста для ошибки
def order_info_check(company_info, order_info):
    print("order_info_check")
    print(company_info, order_info)
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

    if order_info["status"] == "":
        not_info.append("Статус сделки")
    
  
    print(not_info,not_info_order)
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

        bx = Bitrix(webhook)
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
def add_info_order(request, order, type_save):
    webhook = settings.BITRIX_WEBHOOK
    id_bitrix_order = order.id_bitrix
    bx = Bitrix(webhook)
    orders_bx = bx.get_by_ID("crm.deal.fields", [id_bitrix_order])
    # print(orders_bx)
    data_order = {
        "id": id_bitrix_order,
        "fields": {
            "OPPORTUNITY": order.bill_sum,
        },
    }
    orders_bx = bx.call("crm.deal.update", data_order)
    # print(orders_bx)

    pdf = f"{MEDIA_ROOT}/{ order.bill_file_no_signature}"
    # save_multi_file_bx(
    #     bx, pdf, order.id_bitrix, "crm.deal.update", "UF_CRM_1734415894538"
    # )
    pdf_signed = f"{MEDIA_ROOT}/{ order.bill_file}"

    if order.specification.file:
        document_specification = f"{MEDIA_ROOT}/{ order.specification.file}"

    else:
        document_specification = None

    orders = [2]

    # orders_bx = save_file_bx(
    #     bx,
    #     document_specification,
    #     order.id_bitrix,
    #     "crm.deal.update",
    #     "UF_CRM_1734093516769",
    # )

    # print(orders_bx)

    # ТОВАРЫ СДЕЛКИ
    is_order_pros_bx = save_product_order_bx(bx, order, id_bitrix_order)

    # СЧЕТ  СДЕЛКИ
    if order.bill_id_bx:
        invoice = {
            "title": order.bill_name,
            "accountNumber": order.bill_name,
            "opportunity": order.bill_sum,
            # "parentId2": id_bitrix_order,
            "closedate": order.bill_date_stop,
        }
        invoice_bx = bx.call(
            "crm.item.update",
            {"entityTypeId": 31, "id": order.bill_id_bx, "fields": invoice},
        )
    else:
        invoice = {
            "title": order.bill_name,
            "accountNumber": order.bill_name,
            "opportunity": order.bill_sum,
            "parentId2": id_bitrix_order,
            "closedate": order.bill_date_stop,
        }
        # invoice_bx = bx.get_all("crm.item.fields",{"entityTypeId": 31})
        # invoice_bx = bx.get_all("crm.item.list",{"entityTypeId": 31})
        invoice_bx = bx.call("crm.item.add", {"entityTypeId": 31, "fields": invoice})
        invoice_bx_id = invoice_bx["id"]
        order.bill_id_bx = invoice_bx_id
        order.save()


# crm.deal.update UF_CRM_1734093516769
def save_file_bx(bx, file, id_bx, method, field_name):
    with open(file, "rb") as f:
        file_base64 = base64.b64encode(f.read()).decode("utf-8")

    # {
    # 			"id": 12
    # 		},
    # 		{
    # 			"id": 44
    # 		},
    # orders_bx = bx.call(
    #     method,
    #     {
    #         "id": id_bx,
    #         "fields": {
    #             field_name: {

    #                 "fileData": [
    #                     file,
    #                     file_base64,
    #                 ]
    #             }
    #         },
    #     },
    # # )
    # {"fileData": ["test.txt", "dfgdfgdfgh"]},
    # 	{"fileData": ["test2.txt", "dfgdfgdfgh"]}
    orders_bx = bx.call(
        method,
        {
            "id": id_bx,
            "fields": {
                field_name: [
                    {
                        "fileData": [
                            "3",
                            file_base64,
                        ],
                    },
                ]
            },
        },
    )
    return orders_bx


def save_multi_file_bx(bx, file, id_bx, method, field_name):
    with open(file, "rb") as f:
        file_base64 = base64.b64encode(f.read()).decode("utf-8")

    orders_bx1 = bx.get_by_ID("crm.deal.get", [2])
    file_prd = orders_bx1["UF_CRM_1734415894538"]
    print(file_prd)
    arr_old = [
        # {"id": 12},
        # {"id": 44},
        # ["myNewFile.pdf", "...base64_encoded_file_content..."],
    ]
    for file_pr in file_prd:
        file_old = {
            "id": int(file_pr["id"]),
            # "value": { "showUrl":file_pr["showUrl"],"downloadUrl":file_pr["downloadUrl"]},
        }
        arr_old.append(file_old)
    arr = {
        # "valueId": 0,
        "fileData": [
            "333",
            file_base64,
        ],
    }

    arr_old.append(arr)
    print(arr_old)
    ar = (
        {
            "id": id_bx,
            "fields": {
                field_name: arr_old[
                    {
                        "valueId": 0,
                        "fileData": [
                            "file333",
                            file_base64,
                        ],
                    },
                    {
                        "valueId": 0,
                        "fileData": [
                            "3222",
                            file_base64,
                        ],
                    },
                ]
            },
        },
    )
    print(ar)
    orders_bx = bx.call(method, ar)
    print(orders_bx)
    return orders_bx


# add_info_order сохранение товаров  в заказ битрикс
def save_product_order_bx(bx, order, id_bitrix_order):

    product_bx = bx.get_all(
        "crm.item.productrow.fields",
    )
    # product_bx = bx.get_all("catalog.catalog.get",)

    print(product_bx)
    order_products = ProductSpecification.objects.filter(
        specification=order.specification
    )

    order_products_data = []
    for order_products_i in order_products:
        order_info = {
            "ID": order_products_i.id_bitrix,
            "PRODUCT_NAME": order_products_i.product.name,
            "PRICE": order_products_i.price_one,
            "QUANTITY": order_products_i.quantity,
            "RESERVE_QUANTITY": 255,
        }

        # if order_products_i.id_bitrix:
        #     order_info['ID'] = order_products_i.id_bitrix
        order_products_data.append(order_info)
    print(order_products_data)
    data_bx_product = {
        "id": order.id_bitrix,
        "rows": order_products_data,
    }

    product_bx = bx.call("crm.deal.productrows.set", data_bx_product)
    print(product_bx)
    product_bx_get = bx.get_all("crm.deal.productrows.get", {"id": id_bitrix_order})
    print(product_bx_get)
    # if len(orders) == 1:
    #         orders_bx = {orders_bx["ID"]: orders_bx}
    for prod_bx in product_bx_get:
        order_products_okt = order_products.filter(
            product__name=prod_bx["PRODUCT_NAME"]
        )
        order_products_okt.update(id_bitrix=prod_bx["ID"])

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

    return False


# сохранение информации по товарам после 1с
def save_product_info_bx():
    webhook = settings.BITRIX_WEBHOOK
    bx = Bitrix(webhook)


# новые документы после появления точных сроков поставки
def save_new_doc_bx(pdf, pdf_signed):
    webhook = settings.BITRIX_WEBHOOK
    bx = Bitrix(webhook)


# выгрузка в битрикс данных по товарам
def save_params_product_bx(data):
    webhook = settings.BITRIX_WEBHOOK
    bx = Bitrix(webhook)

    return True


# выгрузка в битрикс данных по оплатам
def save_payment_order_bx(data):
    webhook = settings.BITRIX_WEBHOOK
    bx = Bitrix(webhook)

    return True


# выгрузка в битрикс данных по отгурзке товаров
def save_shipment_order_bx(data):
    webhook = settings.BITRIX_WEBHOOK
    bx = Bitrix(webhook)

    return True


# уведомления о повышения цен и валют битрикс
def currency_check_bx():
    webhook = settings.BITRIX_WEBHOOK
    bx = Bitrix(webhook)

    carrency = get_order_carrency_up()
    product = get_product_price_up()

    data_dict = {}
    for carrency_item in carrency:
        data_curr = carrency_item["currency"]
        for item in carrency_item["order"]:
            order = item["specification__order"]
            order_item_data = {
                "order": item["specification__order"],
                "bitrix_id_order": item["specification__order__id_bitrix"],
                "order_product": [],
                "text": "",
            }
            if order not in data_dict:
                order_item_data["currency"] = [data_curr]
                # order_item_data["currency"].append(data_curr)
                data_dict[order] = order_item_data
            else:
                data_dict[order]["currency"].append(data_curr)

    for product_item in product:
        order = product_item["order"]
        if order in data_dict:
            data_dict[order]["order_product"] = product_item["order_product"]
        else:
            data_dict[order] = product_item

    for key, value in data_dict.items():
        if len(value["currency"]) > 0:
            string = ",".join(value["currency"])
            value["text"] = f"Произошло повышение курса {string}. "

        if len(value["order_product"]) > 0:

            if value["text"] != "":
                text = f"Повышены цены на следующие товары:"
                for prod in value["order_product"]:
                    text_prod = f"{prod['prod_name']} - {prod['price_new']}руб."
                    text = f"{text}{text_prod}"
                value["text"] = f'{value["text"]}{text}'
            else:
                text = f" Уведомление о повышении цен на определенные товары!"
                for prod in value["order_product"]:
                    text_prod = f"{prod['prod_name']} — цена была {prod['price_old']} руб., стала {prod['price_new']} руб. (повышение на 3%)"
                    text = f"{text}{text_prod}"
                value["text"] = f'{value["text"]}{text}'

    print(data_dict)
    return True


# дл currency_check_bx получает массив с валютами
def get_order_carrency_up():
    data_order_curr = {}
    data_order_all = []
    currency_list = Currency.objects.exclude(words_code="RUB")

    now = datetime.datetime.now()
    three_days = datetime.timedelta(3)
    in_three_days = now - three_days
    data_old = in_three_days.strftime("%Y-%m-%d")

    for currency in currency_list:
        curr_name = currency.words_code
        old_rate = CurrencyRate.objects.get(currency=currency, date=data_old)
        now_rate = CurrencyRate.objects.get(currency=currency, date=now)
        old_rate_count = old_rate.vunit_rate
        new_rate_count = now_rate.vunit_rate
        difference_count = new_rate_count - old_rate_count
        count_percent = old_rate_count / 100 * 3
        if difference_count > count_percent:
            product_specification = (
                ProductSpecification.objects.filter(
                    product_currency=now_rate.currency,
                )
                .filter(
                    specification__order__status__in=[
                        "PAYMENT",
                    ]
                )
                .distinct("specification__order")
                .values("specification__order", "specification__order__id_bitrix")
                .exclude(specification__order=None)
            )

            data_it = {
                "currency": curr_name,
                "order": product_specification,
            }
            data_order_all.append(data_it)

            data_order_curr[curr_name] = product_specification

    return data_order_all


# для currency_check_bx массив с товарами
def get_product_price_up():
    order = Order.objects.filter(
        status__in=[
            "PAYMENT",
        ]
    )

    data_order_all = []
    for order_item in order:
        order_item_data = {
            "order": order_item.id,
            "bitrix_id_order": order_item.id_bitrix,
            "order_product": [],
            "currency": [],
            "text": "",
        }
        products = ProductSpecification.objects.filter(
            specification=order_item.specification
        )

        for prod in products:
            if prod.product_price_catalog:

                now_price = Price.objects.get(prod=prod.product).rub_price_supplier

                difference_count = now_price - prod.product_price_catalog
                count_percent = prod.product_price_catalog / 100 * 3
                if difference_count > count_percent:
                    data_product = {
                        "prod": prod.product.article_supplier,
                        "prod_name": prod.product.name,
                        "price_old": prod.product_price_catalog,
                        "price_new": now_price,
                    }
                    order_item_data["order_product"].append(data_product)

        if order_item_data["order_product"] != []:

            data_order_all.append(order_item_data)

    return data_order_all
