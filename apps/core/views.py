from itertools import product
import json
from multiprocessing import context
import os
import random
from django.db.models import Prefetch
from django.contrib.postgres.aggregates import ArrayAgg
from django.template import loader
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import OuterRef, Subquery

from apps import client
from apps.client.models import AccountRequisites, Client, Requisites
from apps.core.bitrix_api import get_manager
from apps.core.models import IndexInfoWeb, SeoTextSolutions, SliderMain
from apps.product.models import Cart, CategoryProduct, Price, Product, ProductProperty

from rest_framework import status

from apps.product.models import ProductCart
from apps.core.utils_web import send_email_message, send_email_message_html
from apps.projects_web.models import Project
from apps.supplier.models import Supplier, Vendor
from apps.user.models import AdminUser
from project.settings import EMAIL_BACKEND
from django.db.models import F
from django.db.models.functions import Round


from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_list_or_404, render
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView
from django.views.decorators.clickjacking import (
    xframe_options_exempt,
    xframe_options_sameorigin,
)


# ГЛАВНАЯ


# @xframe_options_sameorigin
def index(request):
    categories = CategoryProduct.objects.filter(is_view_home_web=True).order_by(
        "article_home_web"
    )[0:7]
    projects = Project.objects.filter(is_view_home_web=True).order_by("?")[0:3]
    promo_slider = SliderMain.objects.filter(active=True).order_by("article")
    vendors = Vendor.objects.filter(is_view_index_web=True).order_by("article")

    motrum_in_numbers = IndexInfoWeb.objects.all().last()

    context = {
        "categories": categories,
        "projects": projects,
        "slider": promo_slider,
        "vendors": vendors,
        "motrum_in_numbers": motrum_in_numbers,
    }
    return render(request, "core/index.html", context)


# КОРЗИНА ПОЛЬЗОВАТЕЛЯ
def cart(request):

    cart = request.COOKIES.get("cart")

    if cart:
        cart_qs = Cart.objects.get(id=cart)
        discount_client = 0
        if cart_qs.client:
            client = Client.objects.get(id=cart_qs.client.id)
            discount_client = client.percent
            if discount_client is None:
                discount_client = 0

            requisites = (
                Requisites.objects.filter(client=client)
                .prefetch_related("accountrequisites_set")
                .annotate(
                    accountrequisit=F("accountrequisites__account_requisites"),
                    accountrequisit_id=F("accountrequisites__id"),
                )
            )

        else:
            requisites = None
            client = None

        product_cart_list = ProductCart.objects.filter(cart=cart).values_list(
            "product__id"
        )
        product_cart = ProductCart.objects.filter(cart=cart)

        # prefetch_queryset_property = ProductProperty.objects.filter(
        #     product__in=product_cart_list
        # )

        product = (
            Product.objects.filter(id__in=product_cart_list)
            .select_related(
                "supplier",
                "vendor",
                "category",
                "group",
                "price",
                "stock",
                "stock__lot",
            )
            .prefetch_related(
                Prefetch(
                    "productproperty_set",
                    # queryset=prefetch_queryset_property,
                ),
                Prefetch(
                    "productimage_set",
                ),
            )
            .annotate(
                quantity=product_cart.filter(product=OuterRef("pk")).values(
                    "quantity",
                ),
                id_product_cart=product_cart.filter(product=OuterRef("pk")).values(
                    "id",
                ),
                # sale_price_total=ArrayAgg('price__rub_price_supplier')
                sale_price=Round(
                    F("price__rub_price_supplier")
                    * 0.01
                    * (100 - float(discount_client)),
                    2,
                ),
            )
        )

    else:
        product = None
        cart = None
        account_requisites = None
        discount_client = None
        requisites = None
        client = None

    context = {
        "client": client,
        "product": product,
        "cart": cart,
        "request": request,
        "title": "Корзина",
        "discount_client": discount_client,
        "requisites": requisites,
        # "account_requisites":account_requisites,
    }

    return render(request, "core/cart.html", context)


# def promo_slider(request):


#     return render(request, "core/includes/promo_slider.html", context)
def solutions_all(request):
    projects = Project.objects.filter(is_view_home_web=True).order_by("?")[0:3]
    context = {"projects": projects}
    return render(request, "core/solutions/solutions_all.html", context)


def cobots_all(request):
    projects = Project.objects.filter(is_view_home_web=True).order_by("?")[0:3]

    context = {"projects": projects}
    return render(request, "core/solutions/cobots.html", context)


def solutions_one(request):
    print(111)
    projects = Project.objects.filter(is_view_home_web=True).order_by("?")[0:3]

    seo_test = None
    try:
        seo_test = SeoTextSolutions.objects.get(name_page=solutions_one)
    except SeoTextSolutions.DoesNotExist:
        seo_test = None
    print(234234)
    context = {"seo_test": seo_test, "projects": projects}
    return render(request, "core/solutions/solutions_one.html", context)


def company(request):

    context = {}
    return render(request, "core/company.html", context)


def company_about(request):
    context = {}
    return render(request, "core/about.html", context)

# политика конфиденциальности
def privacy_policy(request):
    print(99999)
    print(99999)
    print(99999)
    print(99999)
    context = {}
    return render(request, "core/privacy_policy.html", context)


def csrf_failure(request, reason=""):
    return render(request, "core/error_pages/403csrf.html")


def permission_denied(request, exception):
    print(403)
    return render(request, "core/error_pages/403.html", status=403)


def page_not_found(request, exception):
    print(404)
    return render(request, "core/error_pages/404.html", status=404)


def server_error(request):
    print(500)
    return render(request, "core/error_pages/500.html", status=500)


def add_admin_okt(request):
    manager_ok = get_manager()
    print(manager_ok)
    if manager_ok:
        context = {"text": "Успешно добавлены менеджеры"}
        return render(request, "core/clean_page_notifications.html", context)
    else:
        context = {"text": "Ошибка. Обратитесь в тех.поддержку"}
        return render(request, "core/clean_page_notifications.html", context)


# EMAIL SEND
# def email_callback(request):
#     if request.method == "POST":
#         body = json.loads(request.body)

#         user_name = body["name"]
#         user_phone = body["phone"]
#         to_manager = os.environ.get("EMAIL_MANAGER_CALLBACK")

#         send_code = send_email_message(
#             "Обратный звонок", f"Имя: {user_name}. Телефон: {user_phone}", to_manager
#         )

#         if send_code:
#             out = {"status": status.HTTP_200_OK}
#         else:
#             out = {"status": status.HTTP_400_BAD_REQUEST}
#         return JsonResponse(out)
#     else:
#         out = {"status": status.HTTP_400_BAD_REQUEST}
#         return JsonResponse(out)


# def email_manager(request):
#     if request.method == "POST":
#         body = json.loads(request.body)

#         client_id = body["client_id"]
#         text_message = body["text_message"]
#         client = Client.objects.get(id=int(client_id))

#         title_email = "Сообщение с сайта от клиента"
#         text_email = f"Клиент: {client.contact_name}Телефон: {client.phone}Сообщение{text_message}"

#         to_manager = client.manager.email
#         html_message = loader.render_to_string(
#             "core/emails/email.html",
#             {
#                 "client_name": client.contact_name,
#                 "client_phone": client.phone,
#                 "text": text_message,
#             },
#         )
#         send_code = send_email_message_html(
#             title_email, text_email, to_manager, html_message=html_message
#         )

#         if send_code:
#             out = {"status": status.HTTP_200_OK}
#         else:
#             out = {"status": status.HTTP_400_BAD_REQUEST}
#         return JsonResponse(out)
#     else:
#         out = {"status": status.HTTP_400_BAD_REQUEST}
#         return JsonResponse(out)
