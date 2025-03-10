from functools import cache
import random
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Prefetch
from django.db.models import Q, F, OrderBy, Case, When, Value

from apps.admin_specification.views import specifications
from apps.client.models import (
    AccountRequisites,
    Client,
    ClientRequisites,
    Order,
    PhoneClient,
    Requisites,
    RequisitesAddress,
    RequisitesOtherKpp,
)
from apps.notifications.models import Notification
from apps.specification.models import ProductSpecification


def index(request):
    title = "Клиенты"
    context = {
        # "contracts": contracts,
        # "title": title,
        # "servise": servise,
    }
    return render(request, "client/index_client.html", context)


# СТРАНИЦЫ ЛК


# МОИ ЗАКАЗЫ
def my_orders(request):
    print(request)
    # current_user = request.user.id

    # cookie = request.COOKIES.get("client_id")
    # client_id = int(cookie)

    # client = Client.objects.get(pk=current_user)

    context = {
        "title": "Личный кабинет | мои заказы",
    }

    return render(request, "client/my_orders.html", context)


# МОИ ДОКУМЕНТЫ
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


# МОИ РЕКВИЗИТЫ
def my_details(request):
    # cookie = request.COOKIES.get("client_id")
    # client_id = int(cookie)
    current_user = request.user.id
    client = Client.objects.get(pk=current_user)
    req = (
        ClientRequisites.objects.filter(client=client)
        .values_list("requisitesotherkpp__id", flat=True)
        .order_by("id")
    )

    requisites = RequisitesOtherKpp.objects.filter(id__in=req).prefetch_related(
        Prefetch("accountrequisites_set"),
        Prefetch("requisitesaddress_set"),
    )

    context = {
        "title": "Личный кабинет | мои реквизиты",
        "details": requisites,
        "requisites": requisites,
    }
    return render(request, "client/my_details.html", context)


# ПЕРСОНАЛЬНЫЕ ДАННЫЕ
def my_contacts(request):
    cookie = request.COOKIES.get("client_id")
    client_id = int(cookie)

    client = Client.objects.get(pk=client_id)
    other_phone_client = PhoneClient.objects.filter(client=client)
    context = {
        "title": "Личный кабинет | мои контакты",
        "client": client,
        "other_phone_client": other_phone_client,
    }
    return render(request, "client/my_contacts.html", context)


# ЗАКАЗ ОТДЕЛЬНАЯ СТРАНИЦА
def order_client_one(request, pk):
    order = Order.objects.get(pk=pk)
    print(order.bill_name)
    if order.bill_name:
        print(order.bill_name)
        product = (
            ProductSpecification.objects.filter(specification=order.specification)
            .select_related(
                "product",
                "product__stock",
                "product__stock__lot",
                "product__price",
            )
            .prefetch_related(
                Prefetch(
                    "product__productproperty_set",
                ),
                Prefetch(
                    "product__productimage_set",
                ),
            )
            .annotate(
                # full_price=(F("price_one") / 100 * F("extra_discount")),
                full_price=F("product__price"),
                sale_price= Case(
                            When(
                                price_one=None,
                                then=("price_one"),
                            ),
                            When(
                                price_one_original_new=None,
                                then=("price_one_original_new"),
                            ))
            )
        )
    else:
        print("order.bill_nameNONE")
        product = (
            ProductSpecification.objects.filter(specification=order.specification)
            .select_related(
                "product",
                "product__stock",
                "product__stock__lot",
                "product__price",
            )
            .prefetch_related(
                Prefetch(
                    "product__productproperty_set",
                ),
                Prefetch(
                    "product__productimage_set",
                ),
            )
            .annotate(
                # full_price=(F("price_one") / 100 * F("extra_discount")),
                # full_price=F("product__price__currency"),
            
            )
        )
    
    
    # print(product)
    product = None
    context = {
        "order": order,
        "product": product,
    }

    return render(request, "client/client_order_one.html", context)
