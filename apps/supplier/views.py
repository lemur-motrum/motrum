import datetime
from locale import LC_ALL, setlocale
import threading
import traceback
from django.shortcuts import render
from regex import D
from apps.client.models import STATUS_ORDER_BITRIX, Order

from apps.core.bitrix_api import add_info_order, currency_check_bx, get_info_for_order_bitrix, get_manager, get_order_carrency_up, get_product_price_up, get_stage_info_bx, get_status_order, save_new_doc_bx
from apps.logs.utils import error_alert
from dal import autocomplete
from django.db.models import Q

from apps.core.models import CalendarHoliday, Currency
from apps.core.tasks import counter_bill_new_year, currency_chek, del_currency, del_void_cart, get_currency, update_currency_price
from apps.core.utils import create_time_stop_specification, image_error_check
from apps.product.models import CurrencyRate, GroupProduct, Product
from apps.specification.models import ProductSpecification, Specification
from apps.specification.tasks import bill_date_stop, specification_date_stop
from apps.supplier.get_utils.iek import get_iek_stock, iek_api
from apps.supplier.get_utils.motrum_nomenclatur import get_motrum_nomenclature
from apps.supplier.get_utils.motrum_storage import get_motrum_storage
from apps.supplier.get_utils.prompower import prompower_api

from apps.supplier.get_utils.veda import veda_api
from apps.supplier.models import SupplierCategoryProductAll, Vendor
from apps.supplier.get_utils.emas import add_group_emas, add_props_emas_product
from apps.supplier.models import SupplierCategoryProduct, SupplierGroupProduct
from apps.supplier.tasks import add_veda
from apps.user.models import AdminUser
from apps.user.utils import upgrade_permission
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from xml.etree import ElementTree, ElementInclude
from pytils import translit
from django.utils.text import slugify
from simple_history.utils import update_change_reason

from apps.user.views import login_bitrix



# тестовая страница скриптов
def add_iek(request):
    title = "TEST"
    error = "file_api_error"
    location = "Получение\сохранение данных o товаратах 1с "
    info = f"titleTEST"
    e = error_alert(error, location, info)
    pdf = None
    pdf_signed = None
    try:

        data = {
            "bitrix_id": "10568",
            "order_products": [
                {
                    "article_motrum": "0011",
                    "date_delivery": "25-02-2025",
                    "reserve": "1",
                    "client_shipment": "0",
                    "date_shipment": "",
                },
            ],
        }
        order = Order.objects.get(id_bitrix=int(data["bitrix_id"]))
        product_spesif = ProductSpecification.objects.filter(
            specification=order.specification
        )
        is_need_new_pdf = False
        for order_products_item in data["order_products"]:

            prod = product_spesif.get(
                product__article=order_products_item["article_motrum"]
            )
            print(prod)
            if order_products_item["date_delivery"]:
                date_delivery = datetime.datetime.strptime(
                    order_products_item["date_delivery"], "%d-%m-%Y"
                ).date()
                if prod.date_delivery_bill != date_delivery:
                    is_need_new_pdf = True

                    prod.date_delivery_bill = date_delivery

            if order_products_item["date_shipment"]:
                if date_shipment != "":
                    date_shipment = datetime.datetime.strptime(
                        order_products_item["date_shipment"], "%d-%m-%Y"
                    ).date()

                    prod.date_shipment = date_shipment

            if order_products_item["reserve"]:
                prod.reserve = int(order_products_item["reserve"])

            if order_products_item["client_shipment"]:
                prod.client_shipment = int(order_products_item["client_shipment"])

            prod.save()

        if is_need_new_pdf:
            if order.requisites.contract:
                is_req = True
            else:
                is_req = False

            type_save = request.COOKIES.get("type_save")
            order_pdf = order.create_bill(
                request,
                is_req,
                order,
                # bill_name,
                None,
                None,
            )
            if order_pdf:
                pdf = request.build_absolute_uri(order.bill_file_no_signature.url)
                pdf_signed = request.build_absolute_uri(order.bill_file.url)

                print(order_pdf)
        
    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        error = "file_api_error"
        location = "Получение\сохранение данных o товаратах 1с "
        info = f"Получение\сохранение данных o товаратах 1с . Тип ошибки:{e}{tr}"
        e = error_alert(error, location, info)
        
    finally:
        # МЕСТО ДЛЯ ОТПРАВКИ ЭТОЙ ЖЕ ИНФЫ В БИТРИКС
        # если есть изденения даты для переделки счета:

        if pdf:
            is_save_new_doc_bx = save_new_doc_bx(order)
            # if is_save_new_doc_bx == False:
            #     birtix_ok = False






    result = 1
    if result:
        pass
    else:
        result = 1
    context = {
        "title": title,
        "result":result
    }
    return render(request, "supplier/supplier.html", context)


# тестовая страница скриптов
def test(request):
    def background_task():
        # Долгосрочная фоновая задача
        iek_api()

    daemon_thread = threading.Thread(target=background_task)
    daemon_thread.setDaemon(True)
    daemon_thread.start()

    title = "Услуги"

    responsets = ["233", "2131"]

    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)


def add_one_c(request):
    title = "Услуги"
   

    responsets = ["233", "2131"]

    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)


# сохранение емас данных первичное из копии сайта фаилы должны лежать на сервере
def save_emas_props(request):

    def background_task():
        # Долгосрочная фоновая задача
        # add_group_emas()
        add_props_emas_product()

    daemon_thread = threading.Thread(target=background_task)
    daemon_thread.setDaemon(True)
    daemon_thread.start()

    responsets = ["233", "2131"]

    context = {
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)


# добавление разрешений админам
def add_permission(request):
    upgrade_permission()
    context = {}
    return render(request, "supplier/supplier.html", context)

def add_stage_bx(request):
    get_stage_info_bx()
    
def add_admin_okt(request):
    get_manager()
    
# добавление праздников вручную
def add_holidays(request):
    import json
    import requests

    year_date = datetime.datetime.now().year
    year = str(year_date)
    url = (
        "https://raw.githubusercontent.com/d10xa/holidays-calendar/master/json/consultant"
        + year
        + ".json"
    )
    r = requests.get(url)
    holidays_dict = r.json()

    try:
        data_bd = CalendarHoliday.objects.get(year=year)
        data_bd.json_date = holidays_dict
        data_bd.save()

    except CalendarHoliday.DoesNotExist:

        data_bd = CalendarHoliday(year=year, json_date=holidays_dict)
        data_bd.save()

    context = {}
    return render(request, "supplier/supplier.html", context)




class VendorAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Vendor.objects.all()

        supplier = self.forwarded.get("supplier", None)
        if supplier:
            qs = qs.filter(supplier=supplier)

        vendor = self.forwarded.get("vendor", None)
        if vendor:
            qs = qs.filter(vendor=vendor)

        return qs


class SupplierCategoryAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = SupplierCategoryProduct.objects.all()

        supplier = self.forwarded.get("supplier", None)
        if supplier:
            qs = qs.filter(supplier=supplier)

        vendor = self.forwarded.get("vendor", None)
        if vendor:
            qs = qs.filter(vendor=vendor)

        return qs


class SupplierGroupAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = SupplierGroupProduct.objects.all()
        supplier = self.forwarded.get("supplier", None)

        if supplier:
            qs = qs.filter(supplier=supplier)

        vendor = self.forwarded.get("vendor", None)
        if vendor:
            qs = qs.filter(vendor=vendor)

        category_supplier = self.forwarded.get("category_supplier", None)
        if category_supplier:
            qs = qs.filter(category_supplier=category_supplier)

        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) | Q(article_name__icontains=self.q)
            )
        return qs


# class SupplierGroupСategoryAutocomplete(autocomplete.Select2QuerySetView):

#     def get_queryset(self):
#         qs = SupplierGroupProduct.objects.all()
#         supplier = self.forwarded.get("supplier", None)

#         if supplier:
#             qs = qs.filter(supplier=supplier)

#         vendor = self.forwarded.get("vendor", None)
#         if vendor:
#             qs = qs.filter(vendor=vendor)

#         category_supplier = self.forwarded.get("category_supplier", None)
#         if category_supplier:
#             qs = qs.filter(category_supplier=category_supplier)

#         if self.q:
#             qs = qs.filter(
#                 Q(name__icontains=self.q)
#                 | Q(article_name__icontains=self.q)
#             )
#         return qs


class SupplierCategoryProductAllAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = SupplierCategoryProductAll.objects.all()
        supplier = self.forwarded.get("supplier", None)
        if supplier:
            qs = qs.filter(supplier=supplier)

        vendor = self.forwarded.get("vendor", None)
        if vendor:
            qs = qs.filter(vendor=vendor)

        category_supplier = self.forwarded.get("category_supplier", None)
        if category_supplier:
            qs = qs.filter(category_supplier=category_supplier)

        group_supplier = self.forwarded.get("group_supplier", None)
        if category_supplier:
            qs = qs.filter(group_supplier=group_supplier)

        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) | Q(article_name__icontains=self.q)
            )

        return qs


class GroupProductAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = GroupProduct.objects.all()
        category_catalog = self.forwarded.get("category_catalog", None)
        if category_catalog:
            qs = qs.filter(category=category_catalog)

        if self.q:
            qs = qs.filter(
                Q(name__icontains=self.q) | Q(article_name__icontains=self.q)
            )
        return qs


