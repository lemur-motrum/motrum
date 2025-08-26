import csv
import datetime
import json
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
    save_file_bx,
    save_new_doc_bx,
    save_payment_order_bx,
    save_shipment_order_bx,
    serch_or_add_info_client,
)
from apps.core.utils_web import (
    send_email_message,
    get_file_path_company_web,
    send_pin_smsru,
    up_int_skafy,
)
from apps.logs.utils import error_alert
from apps.supplier.get_utils.motrum_filters import (
    convert_all_to_text,
    xlsx_props_motrum,
    xlsx_props_motrum_pandas,
    xlsx_to_csv_one_sheet,
)
from apps.supplier.get_utils.replace_newlines_with_commas import xlsx_props
from apps.supplier.get_utils.unimat_pp import (
    export_unimat_prod_for_1c,
    unimat_prompower_api,
)
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
    create_file_props_in_vendor_props2,
    create_time_stop_specification,
    delete_everything_in_folder,
    delete_prop_motrum_item_duble,
    # email_manager_after_new_order_site,
    get_category_prompower,
    image_error_check,
    product_cart_in_file,
    save_file_product,
    send_requests,
    vendor_delta_optimus_after_load,
    create_file_props_in_vendor_props,
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
    VendorPropertyAndMotrum,
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
from apps.supplier.get_utils.instart import pars_instart_xlsx,get_instart_price_stock
from apps.supplier.get_utils.motrum_nomenclatur import (
    get_motrum_nomenclature,
    nomek_test_2,
)
from apps.supplier.get_utils.innovert import get_innovert_xml, save_stock_innovert
from apps.supplier.get_utils.motrum_storage import get_motrum_storage
from apps.supplier.get_utils.prompower import (
    check_group_prompower,
    export_prompower_prod_for_1c,
    pp_aup_doc_name, pp_aup_doc_name, prompower_api,
)

from apps.supplier.get_utils.veda import parse_drives_ru_category, parse_drives_ru_products, save_categories_to_excel, veda_api
from apps.supplier.models import (
    Supplier,
    SupplierCategoryProductAll,
    SupplierPromoGroupe,
    Vendor,
)
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
from project.settings import DOMIAN, MEDIA_ROOT, BITRIX_WEBHOOK, BASE_MANAGER_FOR_BX
from fast_bitrix24 import Bitrix
from fast_bitrix24.server_response import ErrorInServerResponseException


# тестовая страница скриптов
def add_iek(request):
    # from requests.auth import HTTPBasicAuth
    # import logging
    # logging.getLogger('fast_bitrix24').addHandler(logging.StreamHandler())

    # webhook = BITRIX_WEBHOOK
    # bx = Bitrix(webhook)
    # # bs_id_order = 12020
    # # order = Order.objects.get(id_bitrix=12020)
    # orders_bx = bx.get_by_ID("crm.deal.fields", [12020])
    # print(orders_bx)
    prompower = Supplier.objects.get(slug="prompower")
    print(prompower)
    vendors = Vendor.objects.filter(slug="prompower")
    for vendors_item in vendors:
        if vendors_item.slug == "prompower":
            vendoris = vendors_item

    
        # ОБЩАЯ КАТЕГОРИЯ
    def add_category_groupe():
        url = "https://prompower.ru/api/getCategoryGroups"
        headers = {
            "Cookie": "auth.strategy=local; nuxt-session-id=s%3AVh_wHm_Gp554xfQDqHV6CDxDRMUx5ZH6.NDr1rbwGm%2Boj%2FzU5JLtPnug2OErY%2BhDm9%2FCTOi9r0bM"
        }
        response = requests.request(
            "GET",
            url,
            headers=headers,
        )
        data = response.json()

        for data_item in data:

            try:
                categ = SupplierCategoryProduct.objects.get(
                    supplier=prompower,
                    vendor=vendoris,
                    article_name=data_item["id"],
                )
                if categ.name != data_item["title"]:
                    categ.name = data_item["title"]
                    categ.save()

            except SupplierCategoryProduct.DoesNotExist:
                categ = SupplierCategoryProduct(
                    supplier=prompower,
                    vendor=vendoris,
                    article_name=data_item["id"],
                    name=data_item["title"],
                )
                categ.save()

    # получение всех категорий для каталога
    def add_category():
        url = "https://prompower.ru/api/categories"
        headers = {
            "Cookie": "nuxt-session-id=s%3ArUFByHT7pVHJLlRaku2tG74R7byS_LuK.hVBBCnWUOXqkuHRB8%2FgmCu%2BXk1ZLjQMNeYcrdoBb6O8"
        }
        response = requests.request("GET", url, headers=headers)
        data = response.json()

        # категория\группа
        for data_item in data:
            if data_item["groupId"] is not None and data_item["parentId"] is None:
                categ = SupplierCategoryProduct.objects.get(
                    supplier=prompower,
                    vendor=vendoris,
                    article_name=data_item["groupId"],
                )

                # группа
                try:
                    grope = SupplierGroupProduct.objects.get(
                        supplier=prompower,
                        vendor=vendoris,
                        article_name=data_item["id"],
                        # category_supplier=categ,
                        # name=data_item["title"],
                        # slug=data_item["slug"],
                    )
                    if grope.category_supplier != categ:
                        grope.category_supplier = categ

                    if grope.slug != data_item["title"]:
                        grope.name = data_item["title"]

                    if grope.name != data_item["slug"]:
                        grope.slug = data_item["slug"]

                    grope.save()

                except SupplierGroupProduct.DoesNotExist:
                    grope = SupplierGroupProduct(
                        supplier=prompower,
                        vendor=vendoris,
                        article_name=data_item["id"],
                        category_supplier=categ,
                        name=data_item["title"],
                        slug=data_item["slug"],
                    )
                    grope.save()
            check_group_prompower(data_item["id"],grope,None,None)
        # конечная группа
        for data_item_all in data:

            if data_item_all["parentId"] is not None:
                grope = SupplierGroupProduct.objects.get(
                    supplier=prompower,
                    vendor=vendoris,
                    article_name=data_item_all["parentId"],
                )

                try:
                    all_groupe = SupplierCategoryProductAll.objects.get(
                        supplier=prompower,
                        vendor=vendoris,
                        article_name=data_item_all["id"],
                        # name=data_item_all["title"],
                        # slug=data_item_all["slug"],
                    )
                    if all_groupe.name != data_item_all["title"]:
                        all_groupe.name = data_item_all["title"]

                    if all_groupe.slug != data_item_all["slug"]:
                        all_groupe.slug = data_item_all["slug"]

                    if all_groupe.group_supplier != data_item_all["parentId"]:
                        all_groupe.group_supplier = grope
                        all_groupe.category_supplier_id = grope.category_supplier.id

                    all_groupe.save()

                except SupplierCategoryProductAll.DoesNotExist:
                    all_groupe = SupplierCategoryProductAll(
                        supplier=prompower,
                        vendor=vendoris,
                        name=data_item_all["title"],
                        article_name=data_item_all["id"],
                        category_supplier=grope.category_supplier,
                        group_supplier=grope,
                        slug=data_item_all["slug"],
                    )
                    all_groupe.save()
            check_group_prompower(None,None,data_item_all["id"],all_groupe)

    
    
    
    add_category_groupe()
    add_category()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    result = 1
    title = "TEST"
    context = {"title": title, "result": result}
    return render(request, "supplier/supplier.html", context)


def create_xlsx_props_vendor(request):
    
    def background_task():
        items = [
        # {"path" : "props_file/veda.xlsx", "name": "veda", "name-supplier": None},
        {"path": "props_file/delta.xlsx", "name": "delta", "name-supplier": "delta"},
        {"path": "props_file/emas.xlsx", "name": "emas", "name-supplier": "emas"},
        # {"path": "props_file/iek.xlsx", "name": "iek", "name-supplier": None},
        {"path": "props_file/oni.xlsx", "name": "oni", "name-supplier": "iek"},
        {"path": "props_file/optimus.xlsx", "name": "optimus", "name-supplier": "optimus-drive"},
        {"path": "props_file/prompower.xlsx", "name": "prompower", "name-supplier": None},
        {"path": "props_file/unimat.xlsx", "name": "unimat", "name-supplier": None},
    ]
        for item in items:
            create_file_props_in_vendor_props(item["path"], item["name"], item["name-supplier"])
    daemon_thread = threading.Thread(target=background_task)
    daemon_thread.setDaemon(True)
    daemon_thread.start()
    
    result = 1
    title = "TEST"
    context = {"title": title, "result": result}
    return render(request, "supplier/supplier.html", context)

def prompower_prod_for_1c(request):
    def background_task():
        # Долгосрочная фоновая задача
        export_prompower_prod_for_1c()

    daemon_thread = threading.Thread(target=background_task)
    daemon_thread.setDaemon(True)
    daemon_thread.start()

    result = 1
    title = "TEST"
    context = {"title": title, "result": result}
    return render(request, "supplier/supplier.html", context)


def unimat_prod_for_1c(request):
    def background_task():
        # Долгосрочная фоновая задача
        export_unimat_prod_for_1c()
        # get_motrum_nomenclature()

    daemon_thread = threading.Thread(target=background_task)
    daemon_thread.setDaemon(True)
    daemon_thread.start()

    result = 1
    title = "TEST"
    context = {"title": title, "result": result}
    return render(request, "supplier/supplier.html", context)


# тестовая страница скриптов
def test(request):
    def background_task():
        # Долгосрочная фоновая задача
        pass
        # get_motrum_nomenclature()

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


def add_props_motrum(request):
    def background_task():
        # Долгосрочная фоновая задача
        xlsx_props_motrum_pandas()
    

    daemon_thread = threading.Thread(target=background_task)
    daemon_thread.setDaemon(True)
    daemon_thread.start()


    result = 1
    title = "TEST"
    context = {"title": title, "result": result}
    return render(request, "supplier/supplier.html", context)


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

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q))
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


class PromoGroupeAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = SupplierPromoGroupe.objects.all()
        supplier = self.forwarded.get("supplier", None)
        if supplier:
            qs = qs.filter(supplier=supplier)

        vendor = self.forwarded.get("vendor", None)

        if vendor:
            qs = qs.filter(vendor=vendor)
        if self.q:
            qs = qs.filter(Q(name__icontains=self.q))
        return qs


class PromoGroupeProductAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = SupplierPromoGroupe.objects.all()
        supplier = self.forwarded.get("supplier", None)
        if supplier:
            qs = qs.filter(supplier=supplier)

        vendor = self.forwarded.get("vendor", None)
        print("vendor", vendor)
        if vendor:
            qs = qs.filter(vendor=vendor)

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q))
        return qs
