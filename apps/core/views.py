from itertools import product
import json
from multiprocessing import context
import os
import random
from wsgiref.util import request_uri
from django.db.models import Prefetch
from django.contrib.postgres.aggregates import ArrayAgg
from django.template import loader
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.db.models import OuterRef, Subquery
from django.views.decorators.http import require_GET
from apps import client
from apps.client.models import (
    AccountRequisites,
    Client,
    ClientRequisites,
    Requisites,
    RequisitesAddress,
    RequisitesOtherKpp,
)
from apps.core.bitrix_api import get_manager
from apps.core.models import (
    CompanyInfoWeb,
    CompanyPrijectAutoInfoWeb,
    IndexInfoWeb,
    PhotoClientInfoWeb,
    PhotoEmoloeeInfoWeb,
    ReviewsAutoInfoWeb,
    SeoTextSolutions,
    SliderMain,
    TypeDelivery,
)
from apps.product.models import Cart, CategoryProduct, Price, Product, ProductProperty

from rest_framework import status

from apps.product.models import ProductCart
from apps.core.utils_web import send_email_message, send_email_message_html
from apps.projects_web.models import Project
from apps.supplier.models import Supplier, Vendor
from apps.user.models import AdminUser
from project.settings import EMAIL_BACKEND, IS_PROD
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
def index(request):
    categories = CategoryProduct.objects.filter(is_view_home_web=True).order_by(
        "article_home_web"
    )[0:7]
    projects = Project.objects.filter(is_view_home_web=True).order_by("?")[0:3]
    promo_slider = SliderMain.objects.filter(active=True).order_by("article")
    vendors = Vendor.objects.filter(is_view_index_web=True).order_by("article")[0:4]

    motrum_in_numbers = IndexInfoWeb.objects.all().last()
    motrum_in_numbers2 = CompanyInfoWeb.objects.all().last()
    project_in_numbers = CompanyPrijectAutoInfoWeb.objects.all().last()

    context = {
        "categories": categories,
        "projects": projects,
        "slider": promo_slider,
        "vendors": vendors,
        "motrum_in_numbers": motrum_in_numbers,
        "motrum_in_numbers2": motrum_in_numbers2,
        "project_in_numbers": project_in_numbers,
        "meta_title": "Мотрум - оборудование для автоматизации производства",
        "meta_keywords": "оборудование для автоматизации производства",
        "meta_description": "Наша компания предлагает широкий выбор оборудования для автоматизации производства.",
    }
    return render(request, "core/index.html", context)


# КОРЗИНА ПОЛЬЗОВАТЕЛЯ
def cart(request):

    cart = request.COOKIES.get("cart")
    requisites = None
    type_delivery = None
    if cart:
        cart_qs = Cart.objects.get(id=cart)
        discount_client = 0
        if cart_qs.client:
            all_client_info = False
            client_info = False
            req_info = False
            client = Client.objects.get(id=cart_qs.client.id)
            if client.email and client.last_name:
                client_info = True

            # discount_client = client.percent
            # if discount_client is None:
            #     discount_client = 0
            clent_req_kpp = ClientRequisites.objects.filter(client=client)

            if clent_req_kpp.count() > 0:
                clent_req_kpp_arr = clent_req_kpp.values_list("requisitesotherkpp")
                req_kpp = (
                    RequisitesOtherKpp.objects.filter(id__in=clent_req_kpp_arr)
                    .prefetch_related("accountrequisites_set")
                    .annotate(
                        accountrequisit=F("accountrequisites__account_requisites"),
                        accountrequisit_id=F("accountrequisites__id"),
                    )
                )
                req_adress = RequisitesAddress.objects.filter(
                    requisitesKpp__in=clent_req_kpp_arr
                )
                req_adress_arr = req_adress.values_list("id")
                req_acc = AccountRequisites.objects.filter(
                    requisitesKpp__in=clent_req_kpp_arr
                )

                if (
                    req_kpp.count() > 0
                    and req_adress.count() > 0
                    and req_acc.count() > 0
                ):
                    requisites = req_kpp
                    req_info = True

            if req_info and client_info:
                all_client_info = True
                print(type_delivery)
                type_delivery = TypeDelivery.objects.filter(actual=True)
                print(type_delivery)

        else:
            requisites = None
            client = None
            all_client_info = False

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
        all_client_info = False

    context = {
        "client": client,
        "product": product,
        "cart": cart,
        "request": request,
        "title": "Корзина",
        "discount_client": discount_client,
        "requisites": requisites,
        "all_client_info": all_client_info,
        "type_delivery": type_delivery,
        # "account_requisites":account_requisites,
        "meta_title": "Корзина | Мотрум - автоматизация производства",
    }
    print(context)

    return render(request, "core/cart.html", context)


# Контакты
def contact_page(request):
    context = {
        "meta_title": "Контакты | Мотрум - автоматизация производства",
    }
    return render(request, "core/contact.html", context)


# РЕШЕНИЯ ОБЩАЯ
def solutions_all(request):
    projects = Project.objects.filter(is_view_home_web=True).order_by("?")[0:3]
    context = {
        "projects": projects,
        "meta_title": "Решения | Мотрум - автоматизация производства",
    }
    return render(request, "core/solutions/solutions_all.html", context)


# КОБОТЫ ОБЩАЯ
def cobots_all(request):
    # projects = Project.objects.filter(is_view_home_web=True).order_by("?")[0:3]
    projects = Project.objects.filter(is_view_home_web=True,
        category_project__slug__in=[
            "robototehnicheskie-yachejki",
        ]
    ).order_by("?")[0:3]
    context = {
        "projects": projects,
        "meta_title": "Коботы | Мотрум - автоматизация производства",
    }
    return render(request, "core/solutions/cobots.html", context)


# РЕШЕНИЕ ОДНО ОТЛЕЬЕНАЯ СТРАНИЦА
def solutions_one(request):
    url_name = request.resolver_match.url_name
    if url_name == "shkaf-upravleniya":
        cat_slug = "sborka-shu"
    elif url_name == "marking":
        cat_slug = "markirovka-chestnyij-znak"
    else:
        cat_slug = "robototehnicheskie-yachejki"
    
    # projects = Project.objects.filter(is_view_home_web=True).order_by("?")[0:3]
    projects = Project.objects.filter(is_view_home_web=True,
        category_project__slug=cat_slug
    ).order_by("?")[0:3]
    
    seo_test = None
    try:
        seo_test = SeoTextSolutions.objects.get(name_page=solutions_one)
    except SeoTextSolutions.DoesNotExist:
        seo_test = None
    print("234234", request.path_info)

    if request.path_info == "/cobots-palett/":
        meta_title = "Решение для палетизации"
    elif request.path_info == "/cobots-box/":
        meta_title = "Решение для укладки в короб"
    elif request.path_info == "/cobots-packing/":
        meta_title = "Решение для автоматической упаковки"
    elif request.path_info == "/marking/":
        meta_title = "Маркировка"
    elif request.path_info == "/shkaf-upravleniya/":
        meta_title = "Сборка шкафов управления"

    context = {
        "seo_test": seo_test,
        "projects": projects,
        "meta_title": f"{meta_title} | Мотрум - автоматизация производства",
    }
    return render(request, "core/solutions/solutions_one.html", context)


# сертификаты


def certificates_page(request):

    if request.path_info == "/company/detributer-certificate/":
        meta_title = "Сертификаты дистрибьютора"
    elif request.path_info == "/company/certificate-of-conformity/":
        meta_title = "Сертификаты соответствия"
    else:
        meta_title = "Результаты СОУТ"

    context = {
        "meta_title": f"{meta_title} | Мотрум - автоматизация производства",
    }
    return render(request, "core/sertificates/page.html", context)


# КОМПАНИЯ
def company(request):
    projects = Project.objects.filter(is_view_home_web=True).order_by("?")[0:2]
    motrum_in_numbers = CompanyInfoWeb.objects.all().last()
    project_in_numbers = CompanyPrijectAutoInfoWeb.objects.all().last()
    reviews = ReviewsAutoInfoWeb.objects.filter().order_by("?")[0:3]
    photo_client = PhotoClientInfoWeb.objects.all().order_by("article")
    photo_motrum = PhotoEmoloeeInfoWeb.objects.all().order_by("article")

    print("dsadasdas", projects)

    context = {
        "reviews": reviews,
        "projects": projects,
        "motrum_in_numbers": motrum_in_numbers,
        "project_in_numbers": project_in_numbers,
        "photo_client": photo_client,
        "photo_motrum": photo_motrum,
        "meta_title": "Компания Мотрум | Мотрум - автоматизация производства",
    }

    return render(request, "core/company.html", context)


# УДАЛИТЬ
def company_about(request):
    context = {}
    return render(request, "core/about.html", context)


# политика конфиденциальности
def privacy_policy(request):

    context = {
        "meta_title": "Политика конфиденциальности | Мотрум - автоматизация производства",
    }
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

@require_GET
def robots_txt(request):
    if IS_PROD:
        lines = [
            "Disallow: /admin/",
            "Disallow: /website_admin/",
            "Disallow: /okt/",
            "Disallow: /add_admin_okt/",
            "Disallow: /admin_specification/",
            "Disallow: /api/",
            "Disallow: /tinymce/",
            "Disallow: /logs/",
        ]
    else:
        lines = [
            "User-Agent: *",
            "Disallow: /",
        ]

    return HttpResponse("\n".join(lines), content_type="text/plain")

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
