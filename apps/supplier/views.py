import csv
import datetime
from locale import LC_ALL, setlocale
import os
import random
import re
import threading
import traceback
from django.conf import settings
from django.shortcuts import render

from regex import D
import requests
from apps.client.api.serializers import OrderSerializer
from apps.client.models import (
    STATUS_ORDER_BITRIX,
    AccountRequisites,
    Client,
    ClientRequisites,
    DocumentShipment,
    Order,
    PaymentTransaction,
    Requisites,
    RequisitesAddress,
    RequisitesOtherKpp,
)

from apps.core.bitrix_api import (
    add_info_order,
    add_new_order_bx,
    add_new_order_web,
    add_or_get_contact_bx,
    chech_client_other_rec_company,
    currency_check_bx,
    get_contact_order,
    get_id_bd_in_contact_order,
    get_info_for_order_bitrix,
    get_manager,
    get_manager_info,
    get_order_carrency_up,
    get_product_price_up,
    get_stage_info_bx,
    get_status_order,
    get_upd_clirnt_manager,
    remove_file_bx,
    save_new_doc_bx,
    save_payment_order_bx,
    save_shipment_order_bx,
    serch_or_add_info_client,
)
from apps.core.utils_web import (
    send_email_message,
    get_file_path_company_web,
    send_pin_smsru,
)
from apps.logs.utils import error_alert
from dal import autocomplete
from django.db.models import Q

from apps.core.models import CalendarHoliday, Currency
from apps.core.tasks import (
    counter_bill_new_year,
    currency_chek,
    del_currency,
    del_void_cart,
    get_currency,
    old_get_currency,
    update_currency_price,
)
from apps.core.utils import (
    add_new_photo_adress_prompower,
    create_time_stop_specification,
    delete_everything_in_folder,
    image_error_check,
    product_cart_in_file,
    save_file_product,
    send_requests,
    vendor_delta_optimus_after_load,
)
from apps.notifications.models import Notification
from apps.product.models import (
    CurrencyRate,
    GroupProduct,
    Price,
    Product,
    ProductDocument,
    ProductImage,
    ProductProperty,
    Stock,
)
from apps.specification.models import ProductSpecification, Specification
from apps.specification.tasks import bill_date_stop, specification_date_stop
from apps.specification.utils import save_nomenk_doc, save_shipment_doc
from apps.supplier.get_utils.iek import (
    get_iek_stock,
    iek_api,
    update_prod_iek_get_okt,
    update_prod_iek_in_okt,
)
from apps.supplier.get_utils.motrum_nomenclatur import (
    get_motrum_nomenclature,
    nomek_test_2,
)
from apps.supplier.get_utils.motrum_storage import get_motrum_storage
from apps.supplier.get_utils.prompower import prompower_api

from apps.supplier.get_utils.veda import veda_api
from apps.supplier.models import Supplier, SupplierCategoryProductAll, Vendor
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
from apps.vacancy_web.models import Vacancy
from project.settings import DOMIAN, MEDIA_ROOT, BITRIX_WEBHOOK
from fast_bitrix24 import Bitrix


# тестовая страница скриптов
def add_iek(request):
    # from requests.auth import HTTPBasicAuth
    # import logging

    # logging.getLogger('fast_bitrix24').addHandler(logging.StreamHandler())

    # webhook = BITRIX_WEBHOOK
    # bx = Bitrix(webhook)
    # add_new_photo_adress_prompower()

    result = 1
    title = "TEST"
    context = {"title": title, "result": result}
    return render(request, "supplier/supplier.html", context)


# тестовая страница скриптов
def test(request):
    def background_task():
        # Долгосрочная фоновая задача
        get_motrum_nomenclature()

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
