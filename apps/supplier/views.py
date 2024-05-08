from django.shortcuts import render

from apps.supplier.models import Supplier

# Create your views here.
def add_prompower(request):
    title = "Услуги"
    responsets = Supplier.prompower_api()
    
    context = {
        "title": title,
        "responsets": responsets,
    }
    return render(request, "supplier/supplier.html", context)
