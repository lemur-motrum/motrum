import base64
import datetime
import os
from pickle import TRUE
import random
import traceback
from django.conf import settings
from fast_bitrix24 import Bitrix
from django.http import HttpResponseRedirect
from requests import Response


from apps.client.api.serializers import OrderSerializer
from apps.client.models import (
    STATUS_ORDER_BITRIX,
    AccountRequisites,
    ClientRequisites,
    DocumentShipment,
    Order,
    OrderDocumentBill,
    PhoneClient,
    Requisites,
    RequisitesAddress,
    RequisitesOtherKpp,
)
from apps.core.models import Currency, StageDealBx
from apps.core.utils import client_info_bitrix, create_info_request_order_bitrix, save_file_product, save_info_bitrix_after_web
from apps.core.utils_web import get_file_path_company_web
from apps.logs.utils import error_alert
from apps.product.models import Cart, CurrencyRate, Price, Product
from apps.specification.models import ProductSpecification
from apps.user.models import AdminUser
from project.settings import BASE_MANAGER_FOR_BX, MEDIA_ROOT, BITRIX_WEBHOOK


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
                
                adress_document = RequisitesAddress.objects.get(requisitesKpp_id = acc_req.requisitesKpp.id,type_address_bx = data_company["data_commpany"]['adress_type'] )
                
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
                    "adress_document": adress_document.id
                }
                serializer_class = OrderSerializer
                try:
                    order = Order.objects.get(id_bitrix=bs_id_order)
                    cart = order.cart
                    data_order["cart"] = cart.id
                    new_order_web = order.bill_name
                    serializer = serializer_class(order, data=data_order, many=False)
                    next_url = "admin_specification/bx_start.html"
                    context = {
                        "new_order_web":new_order_web,
                        "type_save": "old",
                        "cart": cart.id,
                        "order": order.id,
                        "serializer": data_order,
                    }
                    error = "error"
                    location = "new_order_web"
                    info = f" {order} {bs_id_order} {new_order_web}"
                    e = error_alert(error, location, info)
                    
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
                            "new_order_web": False,
                            "type_save": "new",
                            "cart": cart.id,
                            "order": order.id,
                            "spes": None,
                            "serializer": None,
                        }
                        return (next_url, context, False)
                    else:
                        
                        error = "error"
                        location = "первичное открытие сделки битрикс"
                        info = f" сделка {bs_id_order} {context}{serializer.errors}"
                        e = error_alert(error, location, info)
                        
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
        if adress_item["TYPE_ID"] == "9" or adress_item["TYPE_ID"] == 9:
            adress_item_bx = True
        else:
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
                
            elif type_preset_req == "3":  # ИП
                legal_entity = f'ИП "{v["RQ_LAST_NAME"]} {v["RQ_FIRST_NAME"]} {v["RQ_SECOND_NAME"]}"'
                # tel = v["RQ_PHONE"]
                type_client = "3"
                ogrn = v["RQ_OGRNIP"]
                kpp = None

            elif type_preset_req == "5":  # Физ. лицо
                legal_entity = f'ИП "{v["RQ_LAST_NAME"]} {v["RQ_FIRST_NAME"]} {v["RQ_SECOND_NAME"]}"'
                # tel = v["RQ_PHONE"]
                kpp = None
                type_client = "5"
                ogrn = v["RQ_OGRNIP"]
                kpp = None

            inn = v["RQ_INN"]
            tel = v["RQ_PHONE"]
            id_req = int(v["ID"])

        contract = req_bx_user_feld[0]["UF_CRM_1736854096"]
        contract_date = req_bx_user_feld[0]["UF_CRM_1737611994"]
        adress_type = None
        company_adress_all = []
        for adress in adress_bx:
            not_web_adrees = False
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

            if adress["TYPE_ID"] == "9" or adress["TYPE_ID"] == 9:
                not_web_adrees = True
                adress_type = 9
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
            
            if not_web_adrees == False:
                if adress["TYPE_ID"] == "6" or adress["TYPE_ID"] == 6:
                    adress_type = 6
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
            "adress_type":adress_type,
            "id_bitrix": id_req,
            "id_company": f"{company}{id_req}",
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
                    admin_okt.bitrix_id = manager["ID"]
                    admin_okt.save()
                    photo_manager_bx(manager,admin_okt)
                except AdminUser.DoesNotExist:
                    pass
            elif "UF_USR_1656306737602" in manager:
                try:
                    admin_okt = AdminUser.objects.get(username=manager["UF_USR_1656306737602"])
                    admin_okt.bitrix_id = manager["ID"]
                    admin_okt.save()
                    photo_manager_bx(manager,admin_okt)
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

def photo_manager_bx(manager,admin_okt):
     if "PERSONAL_PHOTO" in manager :
            if "PERSONAL_PHOTO" in manager :
                photo = manager['PERSONAL_PHOTO']
                photo_name = photo.split("/")
                photo_name = photo_name[-1]
                photo_name = f"{admin_okt.id}{photo_name}"
               
                file_path = get_file_path_company_web(None, photo_name)
              
                p = save_file_product(photo, file_path)
                admin_okt.image = file_path
                admin_okt.save()
    
    
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


# ДОБАВЛЕНИЕ ЗАКАЗОВ И ИНФЫ С САЙТА
def add_new_order_web(order):
    try:
        webhook = BITRIX_WEBHOOK
        bx = Bitrix(webhook)
        base_manager = AdminUser.objects.get(email=BASE_MANAGER_FOR_BX)
        order = Order.objects.get(id=154)
        client = order.client
        req = order.requisites
        req_inn = order.requisites.inn
        acc_req = order.account_requisites
        req_kpp = order.account_requisites.requisitesKpp
        adress_web = RequisitesAddress.objects.get(
            requisitesKpp=req_kpp, type_address_bx="web-lk-adress"
        )
     
        all_rec_client = ClientRequisites.objects.filter(client=client).values_list(
            "requisitesotherkpp__requisites", "requisitesotherkpp__id_bitrix"
        )

        # клиент битрикс
        client_bx_id = add_or_get_contact_bx(bx, client, base_manager)
        req, company_bx_id, client_bx_id, req_bx_id, acc_req_bx_id = (
            serch_or_add_info_client(bx, req_inn, acc_req, adress_web, req, client_bx_id, req_kpp, client,base_manager)
        )
        error = "error"
        location = "Сохранение заказа с сайта в  инфо"
        info = f" сделка {order} {req, company_bx_id, client_bx_id, req_bx_id, acc_req_bx_id}"
        e = error_alert(error, location, info)
        
        # ТЕСТ КОМПАНИЯ САЙТ (НЕ ИСПОЛЬЗОВАТЬ) 17826 65406 6850 4254
        # сохранение заказа битркис
        
        order_new_bx_id = add_new_order_bx(bx, req, company_bx_id, req_bx_id, acc_req_bx_id,client_bx_id)
        order.id_bitrix = order_new_bx_id
        order.save()
        
    except Exception as e:
        tr = traceback.format_exc()
        error = "error"
        location = "Сохранение заказа с сайта в битркис"
        info = f" сделка {order} ошибка {e}{tr}"
        e = error_alert(error, location, info)


def serch_or_add_info_client(
    bx, req_inn, acc_req, adress_web, req, client_bx_id, req_kpp, client,base_manager
):
    def _get_company_bx_in_req(company):
        company_bx = bx.get_by_ID("crm.company.get", [company])
        return company_bx

    def _get_accountreq_bx_in_req(req_id, acc_req):
        print(acc_req)
        acc_req_bx = bx.get_all(
            "crm.requisite.bankdetail.list",
            params={
                "filter": {
                    "ENTITY_TYPE_ID": 8,
                    "ENTITY_ID": req_id,
                    "RQ_ACC_NUM": acc_req.account_requisites,
                    "RQ_COR_ACC_NUM": acc_req.kpp,
                    "RQ_BIK": acc_req.bic,
                    "RQ_BANK_NAME": acc_req.bank,
                },
            },
        )
        if len(acc_req_bx) == 1:
            return acc_req_bx[0]["ID"]
        elif len(acc_req_bx) == 0:
            new_acc_req_bx = add_acc_req_bx(
                bx,
                int(req_id),
                acc_req,
            )
            return new_acc_req_bx
        else:
            return acc_req_bx[0]["ID"]
        
    def _get_adress_bx_in_req(req_bx_id, adress_web):

        adress_bx = bx.get_all(
            "crm.address.list",
            params={
                "filter": {"ENTITY_TYPE_ID": 8, "ENTITY_ID": req_bx_id},
            },
        )
        # [{'TYPE_ID': '6', 'ENTITY_TYPE_ID': '8', 'ENTITY_ID': '6652', 'ADDRESS_1': 'проспект Генерала Тюленева', 'ADDRESS_2': '55', 'CITY': 'Ульяновск', 'POSTAL_CODE': '432072', 'REGION': 'городской округ Ульяновск', 'PROVINCE': 'Ульяновская область', 'COUNTRY': 'Россия', 'COUNTRY_CODE': None, 'LOC_ADDR_ID': '11816', 'ANCHOR_TYPE_ID': '4', 'ANCHOR_ID': '17682'}]
        print(adress_bx)

        if len(req_bx) == 1:
            address1_bx = adress_bx["ADDRESS_1"]
            address2_bx = adress_bx["ADDRESS_2"]
            city = adress_bx["CITY"]
            post_code = adress_bx["POSTAL_CODE"]
            region = adress_bx["PROVINCE"]
            country = adress_bx["COUNTRY"]
            # if address1_bx ==
        else:
            pass
    
    def _check_adress_in_web(req_bx_id):
        
        adress_bx_6 = bx.get_all(
            "crm.address.list",
            params={
                "filter": {"TYPE_ID": 6,"ENTITY_TYPE_ID": 8, "ENTITY_ID": req_bx_id},
            },
        )
        print("adress_bx_6",adress_bx_6)
        adress_bx = bx.get_all(
            "crm.address.list",
            params={
                "filter": {"TYPE_ID": 9,"ENTITY_TYPE_ID": 8, "ENTITY_ID": req_bx_id},
            },
        )
        print("adress_bx",adress_bx)
        if len(adress_bx) > 0 :
            return (True)
        else:
            return (False)
        
    # создать компанию - добавить рекыиззит и банк рек и адресс связать с контактом
    def _add_new_all_company(need_sech_company, company_bx_id):
        print("need need_sech_company", need_sech_company)
        if need_sech_company:
            print("need companu")
            id_bx_company = chech_client_other_rec_company(bx, client)
            print(id_bx_company)
            if id_bx_company != None:
                company_bx_id = id_bx_company[0]
            else:
                company_bx_id = add_company_bx(bx, req, req_kpp, adress_web,base_manager)
        print(company_bx_id)
        print(bx, client_bx_id, company_bx_id)
        print(123123)
        chek_add_contact_company(bx, client_bx_id, company_bx_id)
        req_bx_id = add_req_bx(bx, company_bx_id, req, req_kpp)
        # manager_company = company_bx["ASSIGNED_BY_ID"]
        # manager == AdminUser.objects.get(bitrix_id=int(data["manager"]))
        # req.manager = manager
        id_compane_req_inn = f"{company_bx_id}{req_bx_id}"
        req.id_bitrix = int(id_compane_req_inn)
        
        req.save()
        req_kpp.id_bitrix = req_bx_id
        req_kpp.save()
        acc_req_bx_id = add_acc_req_bx(
            bx,
            req_bx_id,
            acc_req,
        )
        print("adress_web",adress_web)
        print(3333)
        adress_bx_id = add_adress_req_bx(bx, adress_web, 9, req_bx_id,False)
        
        
        
        return (req, company_bx_id, client_bx_id, req_bx_id, acc_req_bx_id)

    def _serch_other_info_company(req_bx, req_kpp, req):
        print("_serch_other_info_company", req_kpp.kpp, req_kpp.ogrn)
        company_bx = []
        req_bx_arr = []
        for req_bx_item in req_bx:
            print(req.type_client)
            print(111)
            if req.type_client == "1":
                if req_bx_item["RQ_KPP"] == str(req_kpp.kpp):
                    if req_bx_item["ID"] not in req_bx_arr:
                        req_bx_arr.append(req_bx_item["ID"])
                else:
                    if req_bx_item["ENTITY_ID"] not in company_bx:
                        company_bx.append(req_bx_item["ENTITY_ID"])

            if req.type_client == "3":
                print(req.type_client)
                if req_bx_item["RQ_OGRNIP"] == str(req_kpp.ogrn):
                    if req_bx_item["ID"] not in req_bx_arr:
                        req_bx_arr.append(req_bx_item["ID"])
                else:
                    print("req_bx_item[" "] == str(req_kpp.ogrn):")
                    if req_bx_item["ENTITY_ID"] not in company_bx:
                        company_bx.append(req_bx_item["ENTITY_ID"])

        print("req_bx_arr", req_bx_arr)
        print("company_bx, req_bx_arr", company_bx, req_bx_arr)
        return (company_bx, req_bx_arr)
    
    # обновление инфы если есть точный реквизит 
    def _upd_info_if_one_req():
        # проверка есть ли адресс + получение договора
        is_adress = _check_adress_in_web(req_bx[0]['ID'])
        print("is_adress",is_adress)
        adress_bx_id = add_adress_req_bx(bx, adress_web, 9, req_bx_id,is_adress)
            
        company_bx = _get_company_bx_in_req(company_id)    
        contract = req_bx[0]["UF_CRM_1736854096"]
        contract_date = req_bx[0]["UF_CRM_1737611994"]
        manager_company = company_bx["ASSIGNED_BY_ID"]
        print("contract,contract_date,manager_company", contract,contract_date,manager_company)
        id_compane_req_inn = f"{company_bx_id}{req_bx_id}"
        
        
        data_upd = {
            "id_req_bx":int(id_compane_req_inn),
            "id_req":req.id,
            "contract_date":contract_date,
            "contract":contract,
            "manager":manager_company,
        }
        save_info_bitrix_after_web(data_upd, req)
        req_kpp.id_bitrix = req_bx_id
        req_kpp.save()
        
        tel_bx = req_bx[0]["RQ_PHONE"]
        if tel_bx == "" or tel_bx == None or tel_bx =="None" or tel_bx != req_kpp.tel :
            phone = req_kpp.tel
            upd_req_bx(bx,int(req_bx_id),phone)
        chek_add_contact_company(bx, client_bx_id, company_id)
        acc_req_bx_id =  _get_accountreq_bx_in_req(int(req_bx_id), acc_req) 
            
            
    req_bx = bx.get_all(
        "crm.requisite.list",
        params={
            "filter": {"ENTITY_TYPE_ID": 4, "RQ_INN": req_inn},
        },
    )
    print("req_bx", req_bx)

    # ТАКОЙ РЕКВИЗИТ ЕСТЬ В БИТРИКС
    if len(req_bx) == 1:
        print("!!!ТАКОЙ РЕКВИЗИТ ЕСТЬ В БИТРИКС len(req_bx) == 1")
        company_id = req_bx[0]["ENTITY_ID"]
        req_bx_id = req_bx[0]["ID"]
        company_bx_arr, req_bx_arr = _serch_other_info_company(req_bx, req_kpp, req)
        # ТОЧНО ЭТОТ КОНКРЕТНЫЙ РЕК
        if len(req_bx_arr) == 1:
            print("!!!ТОЧНО ЭТОТ КОНКРЕТНЫЙ РЕК")
            _upd_info_if_one_req()
           
        #НЕ СОВПАЛИ ДОП ДАННЫЕ        
        else:
            print("!!!НЕ СОВПАЛИ ДОП ДАННЫЕ")
            # добавить рек к компании
            if len(company_bx_arr) == 1:
                need_sech_company = False
                company_bx_id = company_bx_arr[0]
            else:
                need_sech_company = True
                company_bx_id = None

            req, company_bx_id, client_bx_id, req_bx_id, acc_req_bx_id = (
                _add_new_all_company(need_sech_company, company_bx_id)
            )

    # НЕСКОЛЬКО таких РЕКВИЗИТ ЕСТЬ В БИТРИКС
    elif len(req_bx) > 1:
        print('НЕСКОЛЬКО таких РЕКВИЗИТ ЕСТЬ В БИТРИКС')
        # есть конретный совпадающий рек 
        company_bx_arr, req_bx_arr = _serch_other_info_company(req_bx, req_kpp, req)
        print(company_bx_arr, req_bx_arr )
        if len(req_bx_arr) == 1:
            _upd_info_if_one_req()
        else:
            # рек к компании которая совпадает
            if len(company_bx_arr) == 1:
                req, company_bx_id, client_bx_id, req_bx_id, acc_req_bx_id = (
                    _add_new_all_company(False, company_bx_arr[0])
                )
            # рек к новой компании
            else:
                req, company_bx_id, client_bx_id, req_bx_id, acc_req_bx_id = (
                    _add_new_all_company(True, None)
                )

    # НОВЫЙ РЕКВИЗИТ ДЯЛ БИТРИКС
    else:
        print("НОВЫЙ РЕКВИЗИТ ДЯЛ БИТРИКС")
        # создать компанию - добавить рекыиззит и банк рек и адресс связать с контактом

        req, company_bx_id, client_bx_id, req_bx_id, acc_req_bx_id = (
            _add_new_all_company(True, None)
        )


    return (req, company_bx_id, client_bx_id, req_bx_id, acc_req_bx_id)


# получение обновление и создание контакта в битрикс - ответ айти битрикс контакта
def add_or_get_contact_bx(bx, client, base_manager):
    name = client.first_name
    last_name = client.last_name
    middle_name = client.middle_name
    phone = client.phone
    email = client.email
    position = client.position
    # phone = "71111111112"
    phone = f"+{phone}"
    phone_st = [f"{phone}"]
    phone_arr = [{"VALUE": phone, "VALUE_TYPE": "WORK"}]
    phone_dop = PhoneClient.objects.filter(client=client)
    if phone_dop.count() > 0:
        for ph in phone_dop:
            phone_new = {"VALUE": f"+{ph.phone}", "VALUE_TYPE": "WORK"}
            phone_arr.append(phone_new)
            phone_st.append(f"+{ph.phone}")
    print(phone_dop)
    # name = "Тест"
    # last_name = "Тест"
    # middle_name = "test"

    # email = "test@test.test"

    contact_bx = bx.get_all(
        "crm.contact.list",
        params={
            "filter": {"NAME": name, "LAST_NAME": last_name, "PHONE": f"{phone}"},
            # "filter": {"NAME": f"ТЕСТ (НЕ ИСПОЛЬЗОВАТЬ){name}", "LAST_NAME": f"ТЕСТ (НЕ ИСПОЛЬЗОВАТЬ){last_name}", "PHONE": f"{phone}"},
            "select": [
                "ID",
                "NAME",
                "LAST_NAME",
                "EMAIL",
                "PHONE",
                "ASSIGNED_BY_ID",
                "SECOND_NAME",
            ],
        },
    )
    print("contact_bx", contact_bx)

    if len(contact_bx) == 1:
        is_phone = False
        need_new_phone = []
        is_email = False
        fields = {}
        if contact_bx[0]["SECOND_NAME"] != middle_name:
            fields["SECOND_NAME"] = middle_name

        if "PHONE" in contact_bx[0]:
            for phones_bx in contact_bx[0]["PHONE"]:
                print(phones_bx["VALUE"])
                print(phone_st)
                if phones_bx["VALUE"] in phone_st:
                    is_phone = True
                    phone_arr.remove(
                        {"VALUE": phones_bx["VALUE"], "VALUE_TYPE": "WORK"}
                    )
                    # need_new_phone.append()

                # if phones_bx["VALUE"] == phone:
                #     is_phone = True
        print("phone_arr", phone_arr)
        if len(phone_arr) > 0:
            # if is_phone == False:
            # fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "WORK"}]
            fields["PHONE"] = phone_arr
        if "EMAIL" in contact_bx[0]:
            for email_bx in contact_bx[0]["EMAIL"]:
                if email_bx["VALUE"] == email:
                    is_email = True

        if is_email == False:
            fields["EMAIL"] = [{"VALUE": email, "VALUE_TYPE": "WORK"}]

        print("fields", fields)
        if fields:
            contact_upd = {"id": contact_bx[0]["ID"], "fields": fields}
            contact_upd_bx = bx.call("crm.contact.update", contact_upd)
        print("contact_bx", contact_bx)
        return contact_bx[0]["ID"]
    else:
        tasks = {
            "fields": {
                "NAME": f"{name}",
                "SECOND_NAME": middle_name,
                "LAST_NAME": f"{last_name}",
                "SOURCE_ID":"146",
                "SOURCE_DESCRIPTION": "Заказ с сайта motrum.ru",
                "POST": position,
                "ASSIGNED_BY_ID": base_manager.bitrix_id,
                "PHONE": phone_arr,
                "EMAIL": [{"VALUE": email, "VALUE_TYPE": "WORK"}],
            }
        }

        contact_bx = bx.call("crm.contact.add", tasks)
        return contact_bx


# СОХДАТЬ КОМПАНИЮ БИТРИКС ВЫХОД ИД БИТРИКС КОМПАНИИ
def add_company_bx(bx, req, req_kpp, adress,base_manager):
    print("add_company_bx")
    company_bx_fields = bx.get_all("crm.company.fields",)
    sity = company_bx_fields['UF_CRM_1558613254']['items']
    province = company_bx_fields['UF_CRM_1724223404']['items']
    adress_city = adress.city
    adress_city_id = ""
    for s in sity:
        if s['VALUE'] == adress_city:
            adress_city_id = s['ID']
    
    adress_province = adress.region
    adress_province_id = ""
    for p in province:
        p_val = p['VALUE'].replace(".", "")
        if p_val == adress_province:
            adress_province_id = p['ID']
    current_date = datetime.date.today().isoformat()
    
    tasks = {
        "fields": {
            "TITLE": f"ТЕСТ (НЕ ИСПОЛЬЗОВАТЬ) САЙТ{req.legal_entity}",
            "COMPANY_TYPE": 'CUSTOMER',
            "PHONE": [{"VALUE": req_kpp.tel, "VALUE_TYPE": "WORK"}] if req_kpp.tel else [],
            "HAS_PHONE": True if req_kpp.tel else False,
            "UF_CRM_1558617084": "44",
            "UF_CRM_1657688354898": "62",
            "UF_CRM_1558613254":adress_city_id,
            "UF_CRM_1724223404":adress_province_id,
            "UF_CRM_1558613176":current_date,
             "ASSIGNED_BY_ID": base_manager.bitrix_id,
            
            
        }
    }
    print(tasks)
    company_bx_new = bx.call("crm.company.add", tasks)
    return company_bx_new


# СОХДАТЬ РЕКВИЗИТ КОМПАНИИ БИТРИКС ВЫХОД ИД БИТРИКС КОМПАНИИ
def add_req_bx(bx, company_bx_id, req, reqKpp):
    print("add_req_bx")
    tasks = {
        "fields": {
            "ENTITY_TYPE_ID": 4,
            "ENTITY_ID": int(company_bx_id),
            "PRESET_ID": int(req.type_client),
            "RQ_INN": req.inn,
            "RQ_PHONE": reqKpp.tel if reqKpp.tel else "",
        }
    }
    if req.type_client == "1":
        tasks["fields"]["NAME"] = "САЙТ Организация"
        tasks["fields"]["RQ_COMPANY_NAME"] = req.legal_entity
        tasks["fields"]["RQ_KPP"] = reqKpp.kpp
        tasks["fields"]["RQ_OGRN"] = reqKpp.ogrn
    elif req.type_client == "3":
        tasks["fields"]["NAME"] = "САЙТ ИП"
        tasks["fields"]["RQ_NAME"] = req.legal_entity
        tasks["fields"]["RQ_FIRST_NAME"] = req.first_name
        tasks["fields"]["RQ_LAST_NAME"] = req.last_name
        tasks["fields"]["RQ_SECOND_NAME"] = req.middle_name
        tasks["fields"]["RQ_OGRNIP"] = reqKpp.ogrn
    else:
        pass
    print(tasks)
    req_bx_new = bx.call("crm.requisite.add", tasks)
    print(req_bx_new)#6790
    return req_bx_new


# СОЗДАТЬ АДРЕСС В БИТРИКС
def add_adress_req_bx(bx, adress, type_id, req_id_bx,is_adress):
    print(" СОЗДАТЬ АДРЕСС В БИТРИКС",adress)
    print("is_adress",is_adress)
    tasks = {
        "fields": {
            "TYPE_ID": 9,
            "ENTITY_TYPE_ID": 8,
            "ENTITY_ID": req_id_bx,
            "ADDRESS_1": adress.address1,
            "ADDRESS_2": adress.address2,
            "CITY": adress.city,
            "POSTAL_CODE": adress.post_code,
            "PROVINCE": adress.region,
            "COUNTRY": adress.country,
        }
    }

    print("tasks", tasks)
    if is_adress:
        print("crm.address.update")
        acc_req_new = bx.call("crm.address.update", tasks) 
        
    else:
        print("crm.address.add")
        acc_req_new = bx.call("crm.address.add", tasks)
    print("acc_req_new", acc_req_new)


# СОЗДАТЬ БАНК РЕКВИЗИТ БИТРИКС
def add_acc_req_bx(
    bx,
    req_id_bx,
    account_requisites,
):
    tasks = {
        "fields": {
            "ENTITY_ID": int(req_id_bx),
            "NAME": f"Сайт реквизиты - {account_requisites.bank}",
            "RQ_ACC_NUM": account_requisites.account_requisites,
            "RQ_BANK_NAME": account_requisites.bank,
            "RQ_COR_ACC_NUM": account_requisites.kpp,
            "RQ_BIK": account_requisites.bic,
        }
    }

    print("tasks", tasks)
    acc_req_new = bx.call("crm.requisite.bankdetail.add", tasks)
    print("acc_req_new", acc_req_new)
    return acc_req_new


# связка контакт реквизит
def chek_add_contact_company(bx, client_bx_id, company_bx_id):
    print("chek_add_contact_company", client_bx_id, company_bx_id)

    contacts = bx.call(
        "crm.contact.company.items.get",
        {
            "id": client_bx_id,
        },
    )
    print("contacts",contacts)
    
    is_need = False
    
    if len(contacts)> 0:
        if contacts["COMPANY_ID"] != int(company_bx_id):
            is_need = True
    else:
        is_need = True
    
    if is_need:
        print("contacts[""] != str(company_bx_id)")
        tasks = {
            "id": client_bx_id,
            "fields": {
                "COMPANY_ID": company_bx_id,
                "IS_PRIMARY": "Y",
            },
        }
        print(tasks)
        contact_company = bx.call("crm.contact.company.add", tasks)
        print("contact_company", contact_company)


# СОЗДАТЬСДЕЛКУ БИТРИКСbx, req, company_bx_id, req_bx_id, acc_req_bx_id,client_bx_id
def add_new_order_bx(bx, req, company_bx_id, req_bx_id, acc_req_bx_id,client_bx_id):
    current_date = datetime.datetime.now().strftime("%d.%m.%Y")
    company_bx = bx.get_by_ID("crm.company.get", [company_bx_id])
    print(company_bx)
    manager_company = company_bx["ASSIGNED_BY_ID"]
    tasks = {
        "fields": {
            "TITLE": f"ТЕСТ (НЕ ИСПОЛЬЗОВАТЬ) Заказ сайт - {req.legal_entity}{current_date}",
            # "TITLE": f"ТЕСТ (НЕ ИСПОЛЬЗОВАТЬ) {req.legal_entity}{current_date}",
            "TYPE_ID": "SALE",
            "CATEGORY_ID": 8,
            "STAGE_ID": "C8:PREPARATION",
            "CURRENCY_ID": "RUB",
            "COMPANY_ID": company_bx_id,
            "ASSIGNED_BY_ID": manager_company,
            "SOURCE_ID":"CALLBACK",
            "SOURCE_DESCRIPTION": "Заказ с сайта motrum.ru",
            "CONTACT_IDS":[client_bx_id],
            "UF_CRM_1715001709654":"848",
        }
    } 
    order_new_bx_id = bx.call("crm.deal.add", tasks)
    print("order_new_bx_id",order_new_bx_id)
    task_req = {
        "fields": {
            "ENTITY_TYPE_ID":2,
            "ENTITY_ID":order_new_bx_id,
            "REQUISITE_ID":req_bx_id,
            "BANK_DETAIL_ID":acc_req_bx_id,
            "MC_REQUISITE_ID":0,
            "MC_BANK_DETAIL_ID":0,
            
        }
    }
    
    add_req_to_order = bx.call("crm.requisite.link.register", task_req)
    
    return order_new_bx_id

    

    


# проверка есть ли компании связаннфе с другими реквизитами клиента - если да значить одна компания
def chech_client_other_rec_company(bx, client):
    all_rec_client = ClientRequisites.objects.filter(client=client)
    print("req_bx")
    all_rec_client_id = []
    all_rec_client_req = []

    for all_rec_client_item in all_rec_client:
        if all_rec_client_item.requisitesotherkpp.id_bitrix:
            all_rec_client_id.append(all_rec_client_item.requisitesotherkpp.id_bitrix)
        if (
            all_rec_client_item.requisitesotherkpp.requisites.inn
            not in all_rec_client_req
        ):
            all_rec_client_req.append(
                int(all_rec_client_item.requisitesotherkpp.requisites.inn)
            )
    print(all_rec_client_id)
    print(all_rec_client_req)
    company_id = []

    # проверка компаний с такимиже итрикс ид как у других реквизитов компании
    if len(all_rec_client_id) > 0:
        req_bx = bx.get_all(
            "crm.requisite.list",
            params={
                "filter": {"ENTITY_TYPE_ID": 4, "ID": all_rec_client_id},
            },
        )
        for req_bx_item in req_bx:
            if (
                req_bx_item["ENTITY_TYPE_ID"] == "4"
                and req_bx_item["ENTITY_ID"] not in company_id
            ):
                company_id.append(req_bx_item["ENTITY_ID"])

    # проверка компаний с такимиже инн  как у других реквизитов компании
    if len(all_rec_client_req) > 0:
        print(all_rec_client_req)
        req_bx = bx.get_all(
            "crm.requisite.list",
            params={
                "filter": {"ENTITY_TYPE_ID": 4, "RQ_INN": all_rec_client_req},
            },
        )
        for req_bx_item in req_bx:
            if (
                req_bx_item["ENTITY_TYPE_ID"] == "4"
                and req_bx_item["ENTITY_ID"] not in company_id
            ):

                company_id.append(req_bx_item["ENTITY_ID"])

    print(company_id)
    if len(company_id) == 1:
        return company_id
    else:
        return None

#обновить данные в реквизите 
def upd_req_bx(bx,reg_bx_id,phone):
    tasks = {
        "id": reg_bx_id,
        "fields": {
            "RQ_PHONE": f"+{phone}",
        }
    }

    print("tasks", tasks)
    acc_req_new = bx.call("crm.requisite.update", tasks)
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
    
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
