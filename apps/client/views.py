from functools import cache
import random
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Prefetch

from apps.client.models import AccountRequisites, Client, Order, Requisites
from apps.notifications.models import Notification


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
    # current_user = request.user.id

    # cookie = request.COOKIES.get("client_id")
    # client_id = int(cookie)

    # client = Client.objects.get(pk=current_user)

    context = {
        "title": "Личный кабинет | мои заказы",
    }

    return render(request, "client/my_orders.html", context)


def my_documents(request):
    current_user = request.user.id
    client = Client.objects.get(pk=current_user)

    # notifications = Notification.objects.filter(
    #     client_id=current_user, is_viewed=False
    # ).exclude(type_notification="STATUS_ORDERING").update(is_viewed=True)

    context = {
        "title": "Личный кабинет | мои документы",
    }
    return render(request, "client/my_documents.html", context)


def my_details(request):
    cookie = request.COOKIES.get("client_id")
    client_id = int(cookie)

    details = Requisites.objects.filter(client=client_id)
    bank_obj = []
    for detail in details:
        my_details = {
            "name": detail.legal_entity,
            "inn": detail.inn,
            "kpp": detail.kpp,
            "ogrn": detail.ogrn,
            "contract": detail.contract,
            "legal_post_code": detail.legal_post_code,
            "legal_city": detail.legal_city,
            "legal_address": detail.legal_address,
            "postal_post_code": detail.postal_post_code,
            "postal_city": detail.postal_city,
            "postal_address": detail.postal_address,
            "bank_details": [],
        }
        bank_details = AccountRequisites.objects.filter(requisites=detail.pk)
        for bank_detail in bank_details:
            bank_object = {
                "account_requisites": bank_detail.account_requisites,
                "bank": bank_detail.bank,
                "kpp": bank_detail.kpp,
                "bic": bank_detail.bic,
            }
            my_details["bank_details"].append(bank_object)

        bank_obj.append(my_details)

    context = {
        "title": "Личный кабинет | мои реквизиты",
        "details": bank_obj,
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
