from functools import cache
import random
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    title = "Клиенты"
    context = {
      
        # "contracts": contracts,
        # "title": title,
        # "servise": servise,
    }
    return render(request, "client/index_client.html", context)

