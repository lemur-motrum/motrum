from django.shortcuts import render


from apps.specification.utils import crete_pdf_specification
from apps.supplier.get_utils.avangard import get_avangard_file
from apps.supplier.get_utils.emas import get_emas
from apps.supplier.get_utils.iek import iek_api
from apps.supplier.get_utils.prompower import prompower_api
from apps.supplier.get_utils.veda import veda_api
from apps.supplier.models import Supplier, SupplierCategoryProduct, SupplierGroupProduct
from apps.user.utils import upgrade_permission

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
    # responsets = ['233','2131']
    responsets = iek_api()
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
    title = "Услуги"
    # responsets = ['233','2131']
    responsets = upgrade_permission()
    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)

from unicodedata import category
from django.shortcuts import render
from dal import autocomplete
from django.db.models import Q
from dal_select2.views import Select2ViewMixin
from dal.views import BaseQuerySetView

from apps.product.models import CategoryProduct, GroupProduct, Product
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
   

       

        return qs
