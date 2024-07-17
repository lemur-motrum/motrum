from django.shortcuts import render


from apps.core.tasks import del_currency, get_currency

from apps.core.utils import create_time
from apps.specification.utils import crete_pdf_specification
from apps.supplier.get_utils.avangard import get_avangard_file
from apps.supplier.get_utils.emas import get_emas
from apps.supplier.get_utils.iek import iek_api
from apps.supplier.get_utils.prompower import prompower_api
from apps.supplier.get_utils.veda import veda_api
from apps.supplier.models import Supplier, SupplierCategoryProduct, SupplierGroupProduct
from apps.user.utils import upgrade_permission
from project.settings import BASE_DIR


# Create your views here.
def add_prompower(request):
    title = "Услуги"
    # responsets = Supplier.prompower_api()
    responsets = prompower_api()
    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)


def add_iek(request):
    title = "Услуги"
   

    # product_list = [product for product.group in product_list  ]
    iek_api()
    responsets = ['233','2131']
    # responsets = 0
    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)


def get_currency_api(request):
    title = "Услуги"
    
    # responsets = ['233','2131']
    responsets
    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)


def get_currency_file(request):
    title = "Услуги"
    # responsets = ['233','2131']
    responsets = get_emas()
    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)


def get_pdf(request):
    title = "Услуги"
    # responsets = ['233','2131']
    responsets = crete_pdf_specification()
    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)


def test(request):
    def save_specification_view_admin():
        from apps.specification.models import ProductSpecification, Specification

        # сохранение спецификации
        id_bitrix = 22  # сюда распарсить значения с фронта
        admin_creator_id = 1  # сюда распарсить значения с фронта

        specification = Specification(
            id_bitrix=id_bitrix,
            admin_creator_id=admin_creator_id,
        )
        specification.save()

        # сохранение продуктов для спецификации

        # массив products имитация массива с фронта в него распирсить значения с фронта
        products = [
            {
                "product_id": 603,
                "quantity": 2,
                "price_exclusive": False,
                "price_one": 100,
            },
            {
                "product_id": 604,
                "quantity": 1,
                "price_exclusive": True,
                "price_one": 222,
            },
        ]

        # перебор продуктов и сохранение
        for product_item in products:
            product = Product.objects.get(id=product_item["product_id"])
            price = Price.objects.get(prod=product)

            # если цена по запросу взять ее если нет взять цену из бд
            if product_item["price_exclusive"] == True:
                price_one = product_item["price_one"]
            else:
                price_one = price.rub_price_supplier

            price_all = int(price_one) * int(product_item["quantity"])

            product_new = ProductSpecification(
                specification=specification,
                product=product,
                product_currency=price.currency,
                quantity=product_item["quantity"],
                price_one=price_one,
                price_all=price_all,
                price_exclusive=product_item["price_exclusive"],
            )
            product_new.save()

        # обновить спецификацию пдф
        pdf = crete_pdf_specification(specification.id)
        Specification.objects.filter(id=specification.id).update(file=pdf)

    title = "Услуги"
    print(124)
    save_specification_view_admin()
    responsets = ["233", "2131"]

    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)

def add_permission(request):
    upgrade_permission()
    context = { 
    }
    return render(request, "supplier/supplier.html", context)


from unicodedata import category
from django.shortcuts import render
from dal import autocomplete
from django.db.models import Q
from dal_select2.views import Select2ViewMixin
from dal.views import BaseQuerySetView

from apps.product.models import CategoryProduct, GroupProduct, Price, Product
from apps.supplier.models import SupplierCategoryProductAll, Vendor


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
        print(qs)

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
        print(qs)

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
            # name__icontains=self.q
            qs = qs.filter(Q(name__icontains=self.q))

        return qs


class GroupProductAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = GroupProduct.objects.all()

        category_catalog = self.forwarded.get("category_catalog", None)

        if category_catalog:
            qs = qs.filter(category=category_catalog)

        return qs
