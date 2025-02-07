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
from apps.client.models import (
    STATUS_ORDER_BITRIX,
    DocumentShipment,
    Order,
    OrderDocumentBill,
)
from apps.core.models import Currency, StageDealBx
from apps.core.utils import client_info_bitrix, create_info_request_order_bitrix
from apps.logs.utils import error_alert
from apps.product.models import Cart, CurrencyRate, Price, Product
from apps.specification.models import ProductSpecification
from apps.user.models import AdminUser
from project.settings import MEDIA_ROOT,BITRIX_WEBHOOK


# проверка данных при открытии iframe в битрикс заказе - проверка реквизитов и заполненности
def get_info_for_order_bitrix(bs_id_order, request):
    try:
        webhook = BITRIX_WEBHOOK
        
        bx = Bitrix(webhook)

        # ПОЛУЧЕНИЕ ДАННЫХ СДЕЛКИ
        orders_bx = bx.get_by_ID("crm.deal.get", [bs_id_order])
        company = orders_bx["COMPANY_ID"]
        name_order_bx = orders_bx["TITLE"]
        if company == "0":
            error_text = "К сделке не прикреплен клиент"
            next_url = "/admin_specification/error-b24/"
            context = {"error": error_text}
            return (next_url, context, True)
        else:  # ПОЛУЧЕНИЕ ДАННЫХ ПОКУПАТЕЛЯ

            company_bx = bx.get_by_ID("crm.company.get", [company])
            manager_company = company_bx["ASSIGNED_BY_ID"]

            data = {
                "order": {
                    "id_bitrix": bs_id_order,
                    "manager": manager_company,
                    "status": orders_bx["STAGE_ID"],
                },
            }
            if manager_company == "":
                error_text = f"У компании не закреплен менеджер"
                next_url = "/admin_specification/error-b24/"
                context = {"error": error_text}
                return (next_url, context, True)
            else:

                try:
                    manager = AdminUser.objects.get(bitrix_id=manager_company)
                except AdminUser.DoesNotExist:
                    next_url = "/admin_specification/error-b24/"
                    error_text = f"Менеджер компании не внесен в окт"
                    context = {"error": error_text}
                    return (next_url, context, True)

            req_error, place, data_company = get_req_info_bx(
                bs_id_order, manager, company
            )
            if req_error:
                error_text = ""
                if place != "Адреса" and place != "Адрес юридический":
                    
                    error_text = f"к сделке не прикреплен {place}"
                else:
                    if place == "Адреса":
                        error_text = f"В выбранных реквизитах не заполнены адреса"
                    elif place == "Адрес юридический":
                        error_text = f"В выбранных реквизитах нет Адрес юридический"
                    else:
                        error_text = f"не заполнен {place}"
                        
                next_url = "/admin_specification/error-b24/"
                context = {"error": error_text}
                return (next_url, context, True)
            error_company, error_order = order_info_check(
                data_company["data_commpany"], data["order"]
            )

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
                print("все данные есть")
                client_req, acc_req = client_info_bitrix(
                    data_company["data_commpany"], data_company["company_adress"]
                )
                status_okt = _status_to_order_replace(
                    data["order"]["status"], bs_id_order
                )

                # try:
                #     manager = AdminUser.objects.get(bitrix_id=manager_company)
                # except AdminUser.DoesNotExist:
                #     manager = AdminUser.objects.filter(admin_type="ALL").first()

                data_order = {
                    "id_bitrix": bs_id_order,
                    "name": int(bs_id_order),
                    "requisites": client_req.id,
                    "account_requisites": acc_req.id,
                    "status": status_okt,
                    "prepay_persent": client_req.prepay_persent,
                    "postpay_persent": client_req.postpay_persent,
                    "manager": manager.id,
                    "text_name": name_order_bx,
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
                        "cart": cart.id,
                        "order": order.id,
                        "serializer": data_order,
                    }
                    if order.specification:
                        context["spes"] = int(order.specification.id)
                    else:
                        context["spes"] = None
                    return (next_url, context, False)
                except Order.DoesNotExist:
                    data["order"]["manager"] = manager
                    cart = Cart.create_cart_admin(None, manager)
                    data_order["cart"] = cart.id
                    serializer = serializer_class(data=data_order, many=False)

                    if serializer.is_valid():
                        next_url = "/admin_specification/current_specification/"
                        serializer._change_reason = "Ручное"
                        order = serializer.save()
                        context = {
                            "type_save": "new",
                            "cart": cart.id,
                            "order": order.id,
                            "spes": None,
                            "serializer": None,
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
        info = f" сделка {bs_id_order} ошибка {e}{tr}"
        e = error_alert(error, location, info)


# для get_info_for_order_bitrix получение реквизитов к сделке
def get_req_info_bx(bs_id_order, manager, company):
    print("get_req_info_bx")
    webhook = BITRIX_WEBHOOK
    bx = Bitrix(webhook)

    # реквизиты привязанные к сделке
    req_bx_order = bx.call(
        "crm.requisite.link.list",
        {"filter": {"ENTITY_TYPE_ID": 2, "ENTITY_ID": bs_id_order}},
    )
    print("req_bx_order", req_bx_order)
    req_bx_id = req_bx_order["REQUISITE_ID"]
    req_acc_bx_id = req_bx_order["BANK_DETAIL_ID"]
    # адреса привязанные к рекуизитам
    adress_bx = bx.get_all(
        "crm.address.list",
        params={
            "filter": {"ENTITY_TYPE_ID": [8], "ENTITY_ID": req_bx_id},
        },
    )
    adress_item_bx = False
    for adress_item in adress_bx:
        if adress_item["TYPE_ID"] == "6" or adress_item["TYPE_ID"] == 6:
            adress_item_bx = True
    
    

    if req_bx_id == "0":
        return (True, "Реквизиты", None)
    elif req_acc_bx_id == "0":
        return (True, "Банковские реквизиты", None)
    elif len(adress_bx) == 0:
        return (True, "Адреса", None)
    elif adress_item_bx == False:
        return (True, "Адрес юридический", None)
    else:

        # значение реквизитов
        req_bx = bx.call(
            "crm.requisite.get",
            {"id": int(req_bx_id)},
        )

        req_bx_user_feld = bx.get_all(
            "crm.requisite.list",
            params={
                "filter": {"ID": req_bx_id},
                "select": ["UF_CRM_1736854096", "UF_CRM_1737611994"],
            },
        )

        for k, v in req_bx.items():
            ogrn = None
            type_preset_req = v["PRESET_ID"]
            if type_preset_req == "1":  # Организация
                legal_entity = v["RQ_COMPANY_NAME"]
                ogrn = v["RQ_OGRN"]
                kpp = v["RQ_KPP"]
                # tel = v["RQ_PHONE"]

                type_client = "1"
            elif type_preset_req == "2":  # ИП
                legal_entity = f'ИП "{v["RQ_LAST_NAME"]} {v["RQ_FIRST_NAME"]} {v["RQ_SECOND_NAME"]}"'
                # tel = v["RQ_PHONE"]
                type_client = "2"
                ogrn = v["RQ_OGRNIP"]
                kpp = None

            elif type_preset_req == "3":  # Физ. лицо
                legal_entity = f'ИП "{v["RQ_LAST_NAME"]} {v["RQ_FIRST_NAME"]} {v["RQ_SECOND_NAME"]}"'
                # tel = v["RQ_PHONE"]
                kpp = None
                type_client = "2"
                ogrn = v["RQ_OGRNIP"]
                kpp = None

            inn = v["RQ_INN"]
            tel = v["RQ_PHONE"]
            id_req = int(v["ID"])

        contract = req_bx_user_feld[0]["UF_CRM_1736854096"]
        contract_date = req_bx_user_feld[0]["UF_CRM_1737611994"]

        company_adress_all = []
        for adress in adress_bx:
            company_adress = {
                "requisitesKpp": None,
                "type_address_bx": adress["TYPE_ID"],
                "country": adress["COUNTRY"],
                "post_code": adress["POSTAL_CODE"],
                "region": adress["REGION"],
                "province": adress["PROVINCE"],
                "city": adress["CITY"],
                "address1": adress["ADDRESS_1"],
                "address2": adress["ADDRESS_2"],
            }
            company_adress_all.append(company_adress)

            if adress["TYPE_ID"] == "6":
                legal_post_code = adress["POSTAL_CODE"]
                bx_city = adress["CITY"]
                bx_city_post = adress["CITY"]

                if (
                    adress["PROVINCE"] != ""
                    or adress["PROVINCE"] != "None"
                    or adress["PROVINCE"] != None
                ):
                    legal_city = f"{adress['PROVINCE']}, г.{adress['CITY']}"
                else:
                    legal_city = f"г.{adress['CITY']},"
                legal_address = f"{adress['ADDRESS_1']},{ adress['ADDRESS_2']}"

                postal_post_code = adress["POSTAL_CODE"]
                postal_city = f"{adress['PROVINCE']}, г.{adress['CITY']}"
                postal_address = f"{adress['ADDRESS_1']},{ adress['ADDRESS_2']}"

            if adress["TYPE_ID"] == "4":
                postal_post_code = adress["POSTAL_CODE"]
                bx_city_post = adress["CITY"]
                if (
                    adress["PROVINCE"] != ""
                    or adress["PROVINCE"] != "None"
                    or adress["PROVINCE"] != None
                ):
                    postal_city = f"{adress['PROVINCE']}, г.{adress['CITY']}"
                else:
                    postal_city = f"г.{adress['CITY']}"
                postal_address = f"{adress['ADDRESS_1']},{ adress['ADDRESS_2']}"

        # банковские реквизиыт привязанные к сделки значение
        req_bank = bx.get_by_ID(
            "crm.requisite.bankdetail.get",
            [req_acc_bx_id],
        )

        account_requisites = req_bank["RQ_ACC_NUM"]
        bank = req_bank["RQ_BANK_NAME"]
        ks = req_bank["RQ_COR_ACC_NUM"]
        bic = req_bank["RQ_BIK"]

        company = {
            "id_bitrix": id_req,
            "manager": manager.id,
            # "legal_entity_motrum": 'ООО ПНМ "Мотрум"',
            "type_client": type_client,
            "contract": contract,
            "contract_date": contract_date,
            "legal_entity": legal_entity,
            "inn": inn,
            "kpp": kpp,
            "ogrn": ogrn,
            "legal_post_code": legal_post_code,
            "legal_city": postal_city,
            "legal_address": postal_address,
            "postal_post_code": postal_post_code,
            "postal_city": postal_city,
            "postal_address": postal_address,
            "tel": tel,
            "account_requisites": account_requisites,
            "bank": bank,
            "ks": ks,
            "bic": bic,
            "postal_post_code": postal_post_code,
            "legal_post_code": legal_post_code,
            "bx_city": bx_city,
            "bx_city_post": bx_city_post,
        }

        context = {
            "data_commpany": company,
            "company_adress": company_adress_all,
        }
        return (False, "All", context)
        # company["legal_entity"] = req_bx["RQ_COMPANY_NAME"]


# для get_info_for_order_bitrix   проверка полей на заполненность при создании заказа-возврат текста для ошибки
def order_info_check(company_info, order_info):
    print("order_info_check")
    print(company_info, order_info)
    not_info = []
    # if company_info["id_bitrix"] == "":
    #     not_info.append("Битрикс номер компании")

    if company_info["legal_entity"] == "":
        not_info.append("Юридическое название клиента")

    if company_info["inn"] == "":
        not_info.append("ИНН")

    if company_info["kpp"] == "" and company_info["type_client"] == 1:
        not_info.append("КПП")

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

    if company_info["postal_post_code"] == "":
        not_info.append("Индекс")

    if company_info["legal_post_code"] == "":
        not_info.append("Индекс")

    if company_info["bx_city"] == "":
        not_info.append("Город")

    if company_info["bx_city_post"] == "":
        not_info.append("Город")

    not_info_order = []

    if order_info["id_bitrix"] == "":
        not_info.append("Битрикс номер сделки")

    if order_info["manager"] == "":
        not_info.append("Менеджер сделки")

    if order_info["status"] == "":
        not_info.append("Статус сделки")

    print(not_info, not_info_order)
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

        webhook = BITRIX_WEBHOOK

        bx = Bitrix(webhook)
        orders = [d["id_bitrix"] for d in actual_order]

        # orders = [1]

        orders_bx = bx.get_by_ID("crm.deal.get", orders)

        if len(orders) == 1:
            orders_bx = {orders_bx["ID"]: orders_bx}

        for order_bx in orders_bx.values():

            print(order_bx)
            id_bx = order_bx["ID"]

            status_bx = order_bx["STAGE_ID"]
            # stage_bd = StageDealBx.objects.get(entity_id="Общая", status_id=status_bx)
            # stage_bd = StageDealBx.objects.get(
            #     entity_id="Квалификация", status_id=status_bx
            # )
            # print("stage_bd", stage_bd)
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
    try:
        webhook = BITRIX_WEBHOOK
        id_bitrix_order = order.id_bitrix
        if id_bitrix_order != 0:
            print("add_info_order")

            bx = Bitrix(webhook)
            orders_bx = bx.get_by_ID("crm.deal.get", [id_bitrix_order])
            if len(orders_bx) > 0:
                orders_bx = bx.get_by_ID("crm.deal.fields", [id_bitrix_order])

                orders_bx = bx.get_by_ID("crm.deal.get", [id_bitrix_order])

                company = orders_bx["COMPANY_ID"]
                company_bx = bx.get_by_ID("crm.company.get", [company])

                order_debt = order.bill_sum - order.bill_sum_paid
                data_order = {
                    "id": id_bitrix_order,
                    "fields": {
                        "OPPORTUNITY": order.bill_sum,
                        "UF_CRM_1734772155723": order.bill_sum_paid,
                        "UF_CRM_1734772173389": order_debt,
                    },
                }
                orders_bx = bx.call("crm.deal.update", data_order)
                print(orders_bx)

                file_dict = OrderDocumentBill.objects.filter(order=order).order_by("id")
                file_dict_signed = file_dict.exclude(bill_file="")
                file_dict_no_signed = file_dict.exclude(bill_file_no_signature="")

                save_multi_file_all_bx(
                    bx,
                    "file_dict_signed",
                    file_dict_signed,
                    id_bitrix_order,
                    "crm.deal.update",
                    "UF_CRM_1734772516954",
                )
                save_multi_file_all_bx(
                    bx,
                    "file_dict_no_signed",
                    file_dict_no_signed,
                    id_bitrix_order,
                    "crm.deal.update",
                    "UF_CRM_1734772537613",
                )

                if order.specification.number:
                    document_specification = f"{MEDIA_ROOT}/{ order.specification.file}"
                    orders_bx = save_file_bx(
                        bx,
                        document_specification,
                        order.id_bitrix,
                        "crm.deal.update",
                        "UF_CRM_1715001959646",
                    )

                else:

                    orders_bx = remove_file_bx(
                        bx,
                        order.id_bitrix,
                        "crm.deal.update",
                        "UF_CRM_1715001959646",
                    )

                # СЧЕТ  СДЕЛКИ

                begindate = datetime.datetime.fromisoformat(
                    order.bill_date_start.isoformat()
                )
                closedate = datetime.datetime.fromisoformat(
                    order.bill_date_stop.isoformat()
                )

                if order.bill_id_bx:
                    invoice = {
                        "title": order.bill_name,
                        "accountNumber": order.bill_name,
                        "opportunity": order.bill_sum,
                        # "parentId2": id_bitrix_order,
                        "begindate": begindate,
                        "closedate": closedate,
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
                        "closedate": closedate,
                    }

                    invoice_bx = bx.call(
                        "crm.item.add", {"entityTypeId": 31, "fields": invoice}
                    )
                    invoice_bx_id = invoice_bx["id"]
                    order.bill_id_bx = invoice_bx_id
                    order.save()
        else:
            error = "file_api_error"
            location = "0- битрикс24"
            info = f"0error"
            e = error_alert(error, location, info)
    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        error = "file_api_error"
        location = "сохранение всех данных по заказу ОКТ- битрикс24"
        info = f"сохранение всех данных по заказу ОКТ- битрикс24:{e}{tr}"
        e = error_alert(error, location, info)


# crm.deal.update UF_CRM_1734093516769
def save_multi_file_all_bx(bx, type_file, file_dict, id_bx, method, field_name):
    print("save_multi_file_all_bx")
    files_arr = []
    for file in file_dict:
        if type_file == "file_dict_signed":
            name = f"{file.from_index}-{file.text_name_bill}"
            if file.is_active == False:
                name = f"{name}_неактуально.pdf"
            else:
                name = f"{name}.pdf"
            file = f"{MEDIA_ROOT}/{ file.bill_file}"

        elif type_file == "file_dict_no_signed":
            name = f"{file.from_index}-{file.text_name_bill_no_sign}"
            if file.is_active == False:
                name = f"{name}_неактуально.pdf"
            else:
                name = f"{name}.pdf"

            file = f"{MEDIA_ROOT}/{ file.bill_file_no_signature}"

        elif type_file == "file_dict_shipment":
            name = file.file

            file = f"{MEDIA_ROOT}/{ file.file}"
        else:
            name = "None"
            file = None

        if file:
            with open(file, "rb") as f:
                file_base64 = base64.b64encode(f.read()).decode("utf-8")

            file_arr = {
                "fileData": [
                    name,
                    file_base64,
                ]
            }

            files_arr.append(file_arr)

    orders_bx = bx.call(
        method,
        {
            "id": id_bx,
            "fields": {field_name: files_arr},
        },
    )


def save_file_bx(bx, file, id_bx, method, field_name):
    print("save_file_bx")
    with open(file, "rb") as f:
        file_base64 = base64.b64encode(f.read()).decode("utf-8")
    # print(file_base64)
    orders_bx = bx.call(
        method,
        {
            "id": id_bx,
            "fields": {
                field_name: {
                    "fileData": [
                        file,
                        file_base64,
                    ],
                },
            },
        },
    )

    return orders_bx


def remove_file_bx(bx, id_bx, method, field_name):

    orders_bx = bx.get_by_ID("crm.deal.get", [id_bx])
    
    if field_name in orders_bx:
        orders_bx_id_file = orders_bx[field_name]["id"]

        orders_bx = bx.call(
            method,
            {
                "id": id_bx,
                "fields": {
                    field_name: {"id": orders_bx_id_file, "remove": "Y"},
                },
            },
        )
    else:
        print("not feald")

    return orders_bx


# новые документы после появления точных сроков поставки
def save_new_doc_bx(order):
    try:
        webhook = BITRIX_WEBHOOK
        bx = Bitrix(webhook)
        error = "file_api_error"
        location = "Получение\сохранение данных o товаратах 1с "
        info = f"{bx}bx"
        e = error_alert(error, location, info)
        id_bitrix_order = order.id_bitrix
        file_dict = OrderDocumentBill.objects.filter(order=order).order_by("id")
        file_dict_signed = file_dict.exclude(bill_file="")
        file_dict_no_signed = file_dict.exclude(bill_file_no_signature="")
        save_multi_file_all_bx(
            bx,
            "file_dict_signed",
            file_dict_signed,
            id_bitrix_order,
            "crm.deal.update",
            "UF_CRM_1734772516954",
        )
        save_multi_file_all_bx(
            bx,
            "file_dict_no_signed",
            file_dict_no_signed,
            id_bitrix_order,
            "crm.deal.update",
            "UF_CRM_1734772537613",
        )
    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        error = "file_api_error"
        location = "Документы с новой датой после 1с б24 "
        info = f"Документы с новой датой после 1с б24. Тип ошибки:{e}{tr}"
        e = error_alert(error, location, info)


# выгрузка в битрикс данных по оплатам
def save_payment_order_bx(data):
    try:

        webhook = BITRIX_WEBHOOK
        bx = Bitrix(webhook)

        for data_item in data:
            order = Order.objects.get(id_bitrix=int(data_item["bitrix_id"]))
            id_bitrix_order = order.id_bitrix
            order_debt = order.bill_sum - order.bill_sum_paid

            data_order = {
                "id": id_bitrix_order,
                "fields": {
                    "UF_CRM_1734772155723": order.bill_sum_paid,
                    "UF_CRM_1734772173389": order_debt,
                },
            }
            orders_bx = bx.call("crm.deal.update", data_order)
    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        error = "file_api_error"
        location = "Отправка данных об оплатах окт - б24 "
        info = f"Отправка данных об оплатах окт - б24. Тип ошибки:{e}{tr}"
        e = error_alert(error, location, info)


# выгрузка в битрикс данных по отгурзке товаров
def save_shipment_order_bx(data):
    try:
        webhook = BITRIX_WEBHOOK
        bx = Bitrix(webhook)
        for data_item in data:
            order = Order.objects.get(id_bitrix=data_item["bitrix_id"])
            id_bitrix_order = order.id_bitrix
            document_shipment = DocumentShipment.objects.filter(order=order).order_by(
                "id"
            )
            save_multi_file_all_bx(
                bx,
                "file_dict_shipment",
                document_shipment,
                id_bitrix_order,
                "crm.deal.update",
                "UF_CRM_1734772575764",
            )

    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        error = "file_api_error"
        location = "Отправка документов выдачи окт - б24 "
        info = f"Отправка документов выдачи  окт - б24. Тип ошибки:{e}{tr}"
        e = error_alert(error, location, info)


# уведомления о повышения цен и валют битрикс
def currency_check_bx():
    try:

        webhook = BITRIX_WEBHOOK
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
                        text_prod = f"{prod['prod_name']} — цена была {prod['price_old']} руб., стала {prod['price_new']} руб. (повышение на {prod['percent_up']}%)"
                        text = f"{text}{text_prod}"
                    value["text"] = f'{value["text"]}{text}'

            save_currency_check_bx(value["text"], value["bitrix_id_order"])

    except Exception as e:
        tr = traceback.format_exc()
        error = "file_api_error"
        location = "отправка в б24 Критичные изменения цен и курса валют"
        info = f"отправка в б24 Критичные изменения цен и курса валют{tr}{e}"
        e = error_alert(error, location, info)


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
                    percent_up = difference_count * 100 / prod.product_price_catalog
                    percent_up = round(percent_up, 2)
                    data_product = {
                        "prod": prod.product.article_supplier,
                        "prod_name": prod.product.name,
                        "price_old": prod.product_price_catalog,
                        "price_new": now_price,
                        "percent_up": percent_up,
                    }
                    order_item_data["order_product"].append(data_product)

        if order_item_data["order_product"] != []:

            data_order_all.append(order_item_data)

    return data_order_all


# для currency_check_bx отпарвка в битрикс данных в сделку
def save_currency_check_bx(info, id_bitrix_order):
    webhook = BITRIX_WEBHOOK
  
    print(webhook)
    bx = Bitrix(webhook)
    data_order = {
        "id": id_bitrix_order,
        "fields": {
            "UF_CRM_1734772618817": info,
        },
    }
    orders_bx = bx.call("crm.deal.update", data_order)


# первичное полуние названий стадий в воронках
def get_stage_info_bx():
    print("get_stage_info_bx")
    try:

        def save_stage_bd(id_stage_var, name_var):
            print("id_stage_var", id_stage_var)
            if int(id_stage_var) == 0:
                filter_status = {
                    # "CATEGORY_ID": id_stage_var,
                    "ENTITY_ID": f"DEAL_STAGE",
                }

            else:
                filter_status = {
                    "CATEGORY_ID": id_stage_var,
                    "ENTITY_ID": f"DEAL_STAGE_{id_stage_var}",
                }
            print(filter_status)
            status_stage_bx = bx.get_all(
                "crm.status.list",
                params={
                    "filter": filter_status,
                },
            )
            print(status_stage_bx)
            for status_stage in status_stage_bx:
                # print(status_stage)
                stage_okt = StageDealBx.objects.get_or_create(
                    bitrix_id=status_stage["ID"],
                    category_id=id_stage_var,
                    defaults={
                        "name": status_stage["NAME"],
                        "entity_id": name_var,
                        # "category_id": status_stage['CATEGORY_ID'],
                        "status_id": status_stage["STATUS_ID"],
                    },
                )
                # print(stage_okt)

        webhook = BITRIX_WEBHOOK
        
        bx = Bitrix(webhook)
        stage_all_bx = bx.get_all(
            "crm.category.list",
            params={
                "entityTypeId": 2,
            },
        )
        print("stage_all_bx", stage_all_bx)

        for stage_one in stage_all_bx:
            print(stage_one)
            id_stage_var = stage_one["id"]
            if stage_one["name"] == "Квалификация":
                save_stage_bd(id_stage_var, stage_one["name"])
            elif stage_one["name"] == "Дистрибьюция":
                save_stage_bd(id_stage_var, stage_one["name"])

            # save_stage_bd(id_stage_var, stage_one["name"])

    except Exception as e:

        tr = traceback.format_exc()
        print(e, tr)
        error = "error"
        location = "Получение статсов битрикс в бд"
        info = f" Получение статсов битрикс в бд {e}{tr}"
        e = error_alert(error, location, info)


#  'ASSIGNED_BY_ID': '1',


def get_manager():

    try:
        webhook = BITRIX_WEBHOOK
        
        bx = Bitrix(webhook)
        manager_all_bx = bx.get_all(
            "user.get",
            params={
                # "entityTypeId": 2,
            },
        )

        for manager in manager_all_bx:
            print(manager)
            if "EMAIL" in manager:
                # if manager["EMAIL"] != "":
                try:
                    admin_okt = AdminUser.objects.get(username=manager["EMAIL"])
                    # admin_okt = AdminUser.objects.filter(email=manager["EMAIL"]).last()
                    admin_okt.bitrix_id = manager["ID"]
                    admin_okt.save()
                    print(manager)
                except AdminUser.DoesNotExist:
                    pass

        return True
    except Exception as e:

        tr = traceback.format_exc()
        print(e, tr)
        error = "error"
        location = "Менеджеры битрикс"
        info = f" Получение Менеджеры битрикс в бд {e}{tr}"
        e = error_alert(error, location, info)
        return False


def _status_to_order_replace(name_status, id_bx):
    status = None
    for choice in STATUS_ORDER_BITRIX:
        if choice[1] == name_status:
            status = choice[0]

            order = Order.objects.filter(id_bitrix=id_bx).last()
            if status == "SHIPMENT_":
                if order:
                    if order.type_delivery == "Самовывоз":
                        status = "SHIPMENT_PICKUP"
                    else:
                        status = "SHIPMENT_AUTO"
                else:
                    # TODO:Как будто не правильно вписывать автошипмент
                    status = "SHIPMENT_AUTO"

    if status:
        return status
    else:

        return "PROCESSING"


# def save_multi_file_bx(bx, file, id_bx, method, field_name):
#     with open(file, "rb") as f:
#         file_base64 = base64.b64encode(f.read()).decode("utf-8")

#     orders_bx1 = bx.get_by_ID("crm.deal.get", [2])
#     file_prd = orders_bx1["UF_CRM_1734415894538"]
#     print(file_prd)
#     arr_old = [
#         # {"id": 12},
#         # {"id": 44},
#         # ["myNewFile.pdf", "...base64_encoded_file_content..."],
#     ]
#     for file_pr in file_prd:
#         file_old = {
#             "id": int(file_pr["id"]),
#             # "value": { "showUrl":file_pr["showUrl"],"downloadUrl":file_pr["downloadUrl"]},
#         }
#         arr_old.append(file_old)
#     arr = {
#         # "valueId": 0,
#         "fileData": [
#             "333",
#             file_base64,
#         ],
#     }

#     arr_old.append(arr)
#     print(arr_old)
#     ar = (
#         {
#             "id": id_bx,
#             "fields": {
#                 field_name: arr_old[
#                     {
#                         "valueId": 0,
#                         "fileData": [
#                             "file333",
#                             file_base64,
#                         ],
#                     },
#                     {
#                         "valueId": 0,
#                         "fileData": [
#                             "3222",
#                             file_base64,
#                         ],
#                     },
#                 ]
#             },
#         },
#     )
#     print(ar)
#     orders_bx = bx.call(method, ar)
#     print(orders_bx)
#     return orders_bx

# add_info_order сохранение товаров  в заказ битрикс
# def save_product_order_bx(bx, order, id_bitrix_order):

#     product_bx = bx.get_all(
#         "crm.item.productrow.fields",
#     )
#     # product_bx = bx.get_all("catalog.catalog.get",)

#     print(product_bx)
#     order_products = ProductSpecification.objects.filter(
#         specification=order.specification
#     )

#     order_products_data = []
#     for order_products_i in order_products:
#         order_info = {
#             "ID": order_products_i.id_bitrix,
#             "PRODUCT_NAME": order_products_i.product.name,
#             "PRICE": order_products_i.price_one,
#             "QUANTITY": order_products_i.quantity,
#             "RESERVE_QUANTITY": 255,
#         }

#         # if order_products_i.id_bitrix:
#         #     order_info['ID'] = order_products_i.id_bitrix
#         order_products_data.append(order_info)
#     print(order_products_data)
#     data_bx_product = {
#         "id": order.id_bitrix,
#         "rows": order_products_data,
#     }

#     product_bx = bx.call("crm.deal.productrows.set", data_bx_product)
#     print(product_bx)
#     product_bx_get = bx.get_all("crm.deal.productrows.get", {"id": id_bitrix_order})
#     print(product_bx_get)
#     # if len(orders) == 1:
#     #         orders_bx = {orders_bx["ID"]: orders_bx}
#     for prod_bx in product_bx_get:
#         order_products_okt = order_products.filter(
#             product__name=prod_bx["PRODUCT_NAME"]
#         )
#         order_products_okt.update(id_bitrix=prod_bx["ID"])

#     # product_bx = bx.get_all("crm.item.productrow.fields",)
#     # product_bx = bx.call(
#     #     "crm.item.productrow.update",
#     #     {
#     #         "id": 30,
#     #         "fields": {
#     #             "price": "1",
#     #         }
#     #     },
#     # )
#     # print(product_bx)

#     # product_bx = bx.call("crm.item.get", data_bx_product)

#     return False


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
