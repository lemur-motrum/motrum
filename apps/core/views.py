import json
import os
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status

from apps.core.utils_web import send_email_message


# Create your views here.
def index(request):

    context = {}
    return render(request, "core/index.html", context)


def okt(request):

    context = {}
    return render(request, "core/okt.html", context)


def web(request):

    context = {}
    return render(request, "core/web.html", context)


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
