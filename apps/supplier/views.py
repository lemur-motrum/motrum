from django.shortcuts import render

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

