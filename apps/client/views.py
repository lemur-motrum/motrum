from functools import cache
import random
from django.http import HttpResponse
from django.shortcuts import render



# from apps.core.utils_web import save_product_cart

# Create your views here.
def index(request):
    title = "Клиенты"
    context = {
      
        # "contracts": contracts,
        # "title": title,
        # "servise": servise,
    }
    return render(request, "client/index_client.html", context)

