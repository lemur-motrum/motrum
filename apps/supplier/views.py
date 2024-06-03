from django.shortcuts import render

from apps.core.currency import del_currency, get_currency, pars, pars_optimums, update_currency_price
from apps.specification.utils import crete_pdf_specification
from apps.supplier.get_utils.avangard import get_avangard_file
from apps.supplier.get_utils.emas import get_emas
from apps.supplier.get_utils.iek import iek_api
from apps.supplier.get_utils.prompower import prompower_api
from apps.supplier.models import Supplier

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
    responsets = get_currency()
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