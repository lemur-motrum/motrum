from itertools import product
import json
import os
from django.template import loader
from django.http import JsonResponse
from django.shortcuts import render

from apps.product.models import CategoryProduct, Product, ProductProperty

from rest_framework import status

from apps.product.models import  ProductCart
from apps.core.utils_web import send_email_message, send_email_message_html
from apps.user.models import AdminUser
from project.settings import EMAIL_BACKEND


nav_elems = [
    {"name": "мои заказы", "link": "my_orders"},
    {"name": "документы", "link": "my_documents"},
    {"name": "мои реквизиты", "link": "my_details"},
    {"name": "мои контакты", "link": "my_contacts"},
]


# Create your views here.
def index(request):
    categories = CategoryProduct.objects.all().order_by("article_name")

    context = {
        "categories": categories,
    }
    return render(request, "core/index.html", context)


def okt(request):

    context = {}

    context = {}
    return render(request, "core/okt.html", context)


def web(request):
    categories = CategoryProduct.objects.all().order_by("article_name")

    context = {
        "categories": categories,
    }
    return render(request, "core/web.html", context)


def my_orders(request):
    nav_elems[0]["active"] = True
    context = {
        "title": "Личный кабинет | мои заказы",
        "nav_elems": nav_elems,
    }
    return render(request, "core/my_orders.html", context)


def my_documents(request):
    nav_elems[1]["active"] = True
    context = {
        "title": "Личный кабинет | мои документы",
        "nav_elems": nav_elems,
    }
    return render(request, "core/my_documents.html", context)


def my_details(request):
    nav_elems[2]["active"] = True
    context = {
        "title": "Личный кабинет | мои реквизиты",
        "nav_elems": nav_elems,
    }
    return render(request, "core/my_details.html", context)


def my_contacts(request):
    nav_elems[3]["active"] = True
    context = {
        "title": "Личный кабинет | мои контакты",
        "nav_elems": nav_elems,
    }
    return render(request, "core/my_contacts.html", context)

def cart(request):
    cart = request.COOKIES.get('cart')
    print(cart)
    product_cart_list = ProductCart.objects.filter(cart=cart).values_list("product__id")
    product_cart_list_count = ProductCart.objects.filter(cart=cart)
    print(product_cart_list)
    
    product = Product.objects.filter(id__in=product_cart_list).select_related(
        "supplier",
        "vendor", 
        "category",
        "group",
        "price",
        "stock",
        )

    context = {"product": product,"cart":cart,}
    
  
    return render(request, "core/cart.html", context)


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
            "core/email.html",
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
