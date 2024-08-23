from functools import cache
import random
from django.http import HttpResponse
from django.shortcuts import render

from apps.client.models import Client, Requisites


# Create your views here.
def index(request):
    title = "Клиенты"
    context = {
        # "contracts": contracts,
        # "title": title,
        # "servise": servise,
    }
    return render(request, "client/index_client.html", context)


def my_orders(request):
    context = {
        "title": "Личный кабинет | мои заказы",
    }
    return render(request, "client/my_orders.html", context)


def my_documents(request):

    context = {
        "title": "Личный кабинет | мои документы",
    }
    return render(request, "client/my_documents.html", context)


def my_details(request):
    cookie = request.COOKIES.get("client_id")
    client_id = int(cookie)

    details = Requisites.objects.filter(client=client_id)

    context = {
        "title": "Личный кабинет | мои реквизиты",
        "details": details,
    }
    return render(request, "client/my_details.html", context)


def my_contacts(request):
    cookie = request.COOKIES.get("client_id")
    client_id = int(cookie)

    client = Client.objects.get(pk=client_id)

    context = {
        "title": "Личный кабинет | мои контакты",
        "client": client,
    }
    return render(request, "client/my_contacts.html", context)
