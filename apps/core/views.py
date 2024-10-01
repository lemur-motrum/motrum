from itertools import product
import json
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
from apps.product.models import Cart, CategoryProduct, Price, Product, ProductProperty

from rest_framework import status

from apps.product.models import ProductCart
from apps.core.utils_web import send_email_message, send_email_message_html
from apps.projects_web.models import Project
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


# ГЛАВНАЯ
def index(request):
    # categories = list(CategoryProduct.objects.all())
    # random.shuffle(categories)
    # cat = categories[0:7]
    categories = CategoryProduct.objects.filter(is_view_home_web=True).order_by("article_home_web")[0:7]
    projects = Project.objects.filter(is_view_home_web=True).order_by("?")[0:3]
    
    context = {
        "categories": categories,
        "projects":projects,
    }
    return render(request, "core/index.html", context)

# ссылки внутренней работы
# def okt(request):
#     context = {}
#     return render(request, "core/okt.html", context)


#КОРЗИНА ПОЛЬЗОВАТЕЛЯ
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
                
            requisites = Requisites.objects.filter(client=client).prefetch_related("accountrequisites_set").annotate(accountrequisit=F('accountrequisites__account_requisites'))
                
                # .prefetch_related("accountrequisites_set")
            # for requisit in requisites:
            #      print(requisit.accountrequisit)
                #    print(requisit.accountrequisites_set.all())
        else:
            requisites = None 
            client = None       
                 

        product_cart_list = ProductCart.objects.filter(cart=cart).values_list("product__id")
        product_cart = ProductCart.objects.filter(cart=cart)

        prefetch_queryset_property = ProductProperty.objects.filter(
            product__in=product_cart_list
        )
        
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
                    queryset=prefetch_queryset_property,
                )
            )
            .annotate(
                quantity=product_cart.filter(product=OuterRef("pk")).values(
                    "quantity",
                ),
                id_product_cart=product_cart.filter(product=OuterRef("pk")).values(
                    "id",
                ),
                # sale_price_total=ArrayAgg('price__rub_price_supplier')
                sale_price=Round(F('price__rub_price_supplier')* 0.01 * (100-float(discount_client)), 2),
  
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
        "client" : client, 
        "product": product,
        "cart": cart,
        "request": request,
        "title": "Корзина",
        "discount_client":discount_client,
        "requisites":requisites,
        # "account_requisites":account_requisites,
    }

    return render(request, "core/cart.html", context)


#политика конфиденциальности
def privacy_policy(request):
    return render(request, "core/privacy_policy.html")



def csrf_failure(request, reason=""):
    return render(request, "core/403csrf.html")


def permission_denied(request, exception):
    print(403)
    return render(request, "core/403.html", status=403)


def page_not_found(request, exception):
    print(404)
    return render(request, "core/404.html", status=404)


def server_error(request):
    print(500)
    return render(request, "core/500.html", status=500)






# EMAIL SEND
def email_callback(request):
    if request.method == "POST":
        body = json.loads(request.body)
        print(body)
        user_name = body["name"]
        user_phone = body["phone"]
        to_manager = os.environ.get("EMAIL_MANAGER_CALLBACK")

        send_code = send_email_message(
            "Обратный звонок", f"Имя: {user_name}. Телефон: {user_phone}", to_manager
        )

        if send_code:
            out = {"status": status.HTTP_200_OK}
        else:
            out = {"status": status.HTTP_400_BAD_REQUEST}
        return JsonResponse(out)
    else:
        out = {"status": status.HTTP_400_BAD_REQUEST}
        return JsonResponse(out)


def email_manager(request):
    if request.method == "POST":
        body = json.loads(request.body)
        print(body)
        client_id = body["client_id"]
        text_message = body["text_message"]
        client = Client.objects.get(id=int(client_id))

        title_email = "Сообщение с сайта от клиента"
        text_email = f"Клиент: {client.contact_name}Телефон: {client.phone}Сообщение{text_message}"

        to_manager = client.manager.email
        html_message = loader.render_to_string(
            "core/emails/email.html",
            {
                "client_name": client.contact_name,
                "client_phone": client.phone,
                "text": text_message,
            },
        )
        send_code = send_email_message_html(
            title_email, text_email, to_manager, html_message=html_message
        )

        if send_code:
            out = {"status": status.HTTP_200_OK}
        else:
            out = {"status": status.HTTP_400_BAD_REQUEST}
        return JsonResponse(out)
    else:
        out = {"status": status.HTTP_400_BAD_REQUEST}
        return JsonResponse(out)
