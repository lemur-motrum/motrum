import json
import os
from django.template import loader
from django.http import JsonResponse
from django.shortcuts import render

from apps.product.models import CategoryProduct

from rest_framework import status

from apps.client.models import Client
from apps.core.utils_web import send_email_message, send_email_message_html
from apps.user.models import AdminUser
from project.settings import EMAIL_BACKEND


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
