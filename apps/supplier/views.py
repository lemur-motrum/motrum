import datetime
from locale import LC_ALL, setlocale
import threading
import traceback
from django.conf import settings
from django.shortcuts import render
from regex import D
from apps.client.models import STATUS_ORDER_BITRIX, DocumentShipment, Order, PaymentTransaction

from apps.core.bitrix_api import add_info_order, currency_check_bx, get_info_for_order_bitrix, get_manager, get_order_carrency_up, get_product_price_up, get_stage_info_bx, get_status_order, remove_file_bx, save_new_doc_bx, save_payment_order_bx, save_shipment_order_bx
from apps.logs.utils import error_alert
from dal import autocomplete
from django.db.models import Q

from apps.core.models import CalendarHoliday, Currency
from apps.core.tasks import counter_bill_new_year, currency_chek, del_currency, del_void_cart, get_currency, update_currency_price
from apps.core.utils import create_time_stop_specification, image_error_check, product_cart_in_file, vendor_delta_optimus_after_load
from apps.product.models import CurrencyRate, GroupProduct, Product
from apps.specification.models import ProductSpecification, Specification
from apps.specification.tasks import bill_date_stop, specification_date_stop
from apps.specification.utils import save_shipment_doc
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
from project.settings import MEDIA_ROOT
from fast_bitrix24 import Bitrix


# тестовая страница скриптов
def add_iek(request):
    from dateutil.parser import parse
    title = "TEST"
    

    iek_api()
    
    # req_bx_order = bx.call(
    #     "crm.requisite.link.list",
    #     {"filter": {"ENTITY_TYPE_ID": 2, "ENTITY_ID": bs_id_order}},
    # )
    # req_bx_user_feld = bx.get_all(
    #         "crm.requisite.list",
    #         params={
    #             "filter": {"RQ_INN": 6316195950},
    #         },
    #     )
 
    # print(req_bx_user_feld)#{'ID': '6650', 'ENTITY_TYPE_ID': '4', 'ENTITY_ID': '17682', 
    
    
    
    
    
    
    # cart = 298
    # new_dir = "{0}/{1}/{2}".format(MEDIA_ROOT,"documents", "kp_file")
    # path_kp = f"{new_dir}/КП.xlsx"
    # # cart = 667
    # def background_task():
    #     # Долгосрочная фоновая задача
    #     product_cart_in_file(path_kp,cart)

    # daemon_thread = threading.Thread(target=background_task)
    # daemon_thread.setDaemon(True)
    # daemon_thread.start()
    # print(daemon_thread.is_alive())
    
    
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

def add_vendor_delta_optimus_after_load(request):
    vendor_delta_optimus_after_load()
    responsets = ["233", "2131"]

    context = {
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)
    
# сохранение емас данных первичное из копии сайта фаилы должны лежать на сервере
def save_emas_props(request):

    def background_task():
        # Долгосрочная фоновая задача
        add_group_emas()
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
    
# def add_admin_okt(request):
#     get_manager()
    
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


