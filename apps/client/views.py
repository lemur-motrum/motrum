from functools import cache
import random
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Prefetch
from django.db.models import Q, F, OrderBy, Case, When, Value
from django.db.models.functions import Round
from django.db.models import Sum
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
    is_final_price = False

    print("order.bill_name", order.bill_name)
    if order.bill_name:
        is_final_price = True
        print(" TRUE")
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
                bill_name=F("specification__order__bill_name"),
                sale_price=F("price_one"),
                full_price=Case(
                    When(
                        extra_discount=None,
                        then=("sale_price"),
                    ),
                    When(
                        extra_discount__isnull=False,
                        then=Round(F("sale_price") / (100 - F("extra_discount")) * 100),
                    ),
                ),
                
                price_all_item=F("price_all"),
                sum_full_price = Round(F("full_price") * F("quantity"))
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
                bill_name=F("specification__order__bill_name"),
                sale_price=F("price_one"),
                sale_price_all=Round(F("price_one") * F("quantity")),
              
                full_price=Case(
                    When(
                        extra_discount=None,
                        then=("sale_price"),
                    ),
                    When(
                        extra_discount__isnull=False,
                        then=Round(F("sale_price") / (100 - F("extra_discount")) * 100),
                    ),
                ),
                price_all_item=F("price_all"),
                sum_full_price = Round(F("full_price") * F("quantity"))
            )
        )

    total_full_price = product.aggregate(
        all_sum_sale_price=Sum("price_all_item"),
        
        all_sum_full_price=Sum("sum_full_price"),
        
        
        all_sum_sale=Round(F("all_sum_sale_price") - F("all_sum_full_price")),
    )
    total_full_price['all_sum_sale'] = abs(total_full_price['all_sum_sale'])
 
    context = {
        "order": order,
        "product": product,
        "is_final_price": is_final_price,
        "total_full_price": total_full_price,
    }

    return render(request, "client/client_order_one.html", context)
