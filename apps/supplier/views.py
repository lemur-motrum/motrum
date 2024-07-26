import datetime
import threading
from django.shortcuts import render
from dal import autocomplete
from django.db.models import Q

from apps.core.models import CalendarHoliday
from apps.product.models import GroupProduct
from apps.supplier.models import SupplierCategoryProductAll, Vendor
from apps.supplier.get_utils.emas import add_group_emas, add_props_emas_product
from apps.supplier.models import SupplierCategoryProduct, SupplierGroupProduct
from apps.supplier.tasks import add_veda
from apps.user.utils import upgrade_permission


def add_iek(request):
    from django.db.models import Prefetch

    title = "Услуги"
    add_veda()

    responsets = ["233", "2131"]
    # responsets = 0
    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)


def test(request):

    title = "Услуги"
    print(124)

    responsets = ["233", "2131"]

    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)


def save_emas_props(request):
    def background_task():
            # Долгосрочная фоновая задача
            add_group_emas()
            add_props_emas_product()

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


def add_permission(request):
    upgrade_permission()
    context = {}
    return render(request, "supplier/supplier.html", context)

def add_holidays(request):
    import json
    import requests
    year_date = datetime.datetime.now().year
    year = str(year_date)
    
    try:
        data_bd = CalendarHoliday.objects.get(year=year)
        data_bd.json_date = holidays_dict
        data_bd.save()
   
    except CalendarHoliday.DoesNotExist:
        url = (
            "https://raw.githubusercontent.com/d10xa/holidays-calendar/master/json/consultant"
            + year
            + ".json"
        )
        r = requests.get(url)
        holidays_dict = r.json()
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

        return qs


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
            qs = qs.filter(Q(name__icontains=self.q))

        return qs


class GroupProductAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = GroupProduct.objects.all()
        category_catalog = self.forwarded.get("category_catalog", None)
        if category_catalog:
            qs = qs.filter(category=category_catalog)

        return qs
