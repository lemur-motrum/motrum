import traceback

from rest_framework import routers, serializers, viewsets, mixins, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.client.models import Client
from apps.core.models import UpdatedCompanyBX24
from apps.core.utils_web import send_email_message_html
from apps.logs.utils import error_alert
from apps.notifications.models import Notification


class Bitrix24ViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = None

    http_method_names = ["get", "post", "put"]

    @action(detail=False, methods=["post"], url_path=r"client-b24")
    def client_b24(self, request, *args, **kwargs):
        try:
            data = request.data
            application_token = data.get("auth[application_token]")
            if application_token:
                companu = data.get("data[FIELDS][ID]")
                obj, created = UpdatedCompanyBX24.objects.get_or_create(
                    company_bx_id=int(companu)
                )

        except Exception as e:
            print(e)
            tr = traceback.format_exc()
            error = "file_api_error"
            location = "ERROR Исходящий вебхук изменение данных компании (менеджера))"
            info = (
                f"ERROR Исходящий вебхук изменение данных компании (менеджера)){e}{tr}"
            )
            e = error_alert(error, location, info)

class FormWebViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.none()
    serializer_class = None

    http_method_names = ["get", "post", "put"]
    
    
    @action(detail=False, methods=["post"], url_path=r"send-form-callback")
    def send_form_callback(self, request, *args, **kwargs):
        from django.template import loader

        data = request.data

        name = data["name"]
        phone = data["phone"]
        url = data["url"]

        # data = {
        #     "name":"Имя",
        #     "phone":"телефон в формате 79999999999"
        # }

        html_message = loader.render_to_string(
            "core/emails/email_callback.html",
            {
                "name": name,
                "phone": phone,
                "url": url,
            },
        )

        subject = "Заявка с формы \"Обратный звонок\" с сайта motrum.ru"
        to_email = "pmn20@motrum.ru"
        # to_email = "lars1515@yandex.ru"

        sending_result = send_email_message_html(subject, None, to_email, html_message=html_message)

        if data and sending_result:
            return Response("ok", status=status.HTTP_200_OK)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["post"], url_path=r"send-form-demo-visit")
    def send_form_demo_visit(self, request, *args, **kwargs):
        from django.template import loader
        from apps.core.bitrix_api import create_lead_from_form

        data = request.data

        name = data["name"]
        phone = data["phone"]
        type = data["type"]
        url = data["url"]

        if type == "cobots-palett":
            page = "Решение для паллетизации"
            manager_id = 28
            is_cobots = True
        elif type == "cobots-box":
            page = "Решение для укладки в короб"
            manager_id = 28
            is_cobots = True
        else:
            page = "Общая страница коботов"
            manager_id = 28
            is_cobots = True

        lead_data = {
            "name": name,
            "phone": phone,
            "page": page,
            "manager_id": manager_id,
        }

        # print(data)
        # type = cobots-palett
        # cobots-box
        # cobots-packing
        # marking
        # shkaf-upravleniya

        create_lead_from_form(lead_data)

        # data = {
        #     "type":"страница с которой демо выезд ",
        #     "name":"Имя",
        #     "phone":"телефон в формате 79999999999"
        # }

        html_message = loader.render_to_string(
            "core/emails/email_demo_visit.html",
            {
                "name": name,
                "phone": phone,
                "page": page,
                "url": url,
            },
        )

        subject = "Заявка с формы \"Демо выезд\" со страницы \"Коботы\" с сайта motrum.ru"
        to_email = "pmn4@motrum.ru"
        # to_email = "lars1515@yandex.ru"

        sending_result = send_email_message_html(subject, None, to_email, html_message=html_message)
        if data and sending_result:
            return Response("ok", status=status.HTTP_200_OK)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["post"], url_path=r"send-form-calculate-project")
    def send_form_calculate_project(self, request, *args, **kwargs):
        from django.template import loader

        data = request.data

        name = data["name"]
        phone = data["phone"]
        url = data["url"]

        # data = {
        #     "name":"Имя",
        #     "phone":"телефон в формате 79999999999"
        # }

        html_message = loader.render_to_string(
            "core/emails/email_calculate_project.html",
            {
                "name": name,
                "phone": phone,
                "url": url,
            },
        )

        subject = "Заявка с формы \"Рассчитать проект\" с сайта motrum.ru"
        to_email = "pmn20@motrum.ru"
        # to_email = "lars1515@yandex.ru"

        sending_result = send_email_message_html(subject, None, to_email, html_message=html_message)

        if data and sending_result:
            return Response("ok", status=status.HTTP_200_OK)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["post"], url_path=r"send-form-company-consultation")
    def send_form_company_consultation(self, request, *args, **kwargs):
        from django.template import loader

        data = request.data

        name = data["name"]
        phone = data["phone"]
        url = data["url"]

        # data = {
        #     "name":"Имя",
        #     "phone":"телефон в формате 79999999999"
        # }

        html_message = loader.render_to_string(
            "core/emails/email_calculate_project.html",
            {
                "name": name,
                "phone": phone,
                "url": url,
            },
        )

        subject = "Заявка с формы \"Нужна консультация\" с сайта motrum.ru"
        to_email = "pmn20@motrum.ru"
        # to_email = "lars1515@yandex.ru"

        sending_result = send_email_message_html(subject, None, to_email, html_message=html_message)

        if data and sending_result:
            return Response("ok", status=status.HTTP_200_OK)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["post"], url_path=r"send-form-manager")
    def send_form_manager(self, request, *args, **kwargs):
        data = request.data
        data = {
            "manager": "айди менеджера число"
            # "name":"Имя",
            # "phone":"телефон в формате 79999999999" 
        }
        if data:
            return Response("ok", status=status.HTTP_200_OK)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["post"], url_path=r"send-form-contact-us")
    def send_form_contact_us(self, request, *args, **kwargs):
        from django.template import loader

        data = request.data

        name = data["name"]
        phone = data["phone"]
        message = data["message"]
        url = data["url"]

        # data = {
        #
        #     "name":"Имя",
        #     "phone":"телефон в формате 79999999999",
        #     "message":"Текст"
        # }

        html_message = loader.render_to_string(
            "core/emails/email_contact_us.html",
            {
                "name": name,
                "phone": phone,
                "message": message,
                "url": url,
            },
        )

        subject = "Заявка со страницы \"Контакты\" с сайта motrum.ru"
        to_email = "pmn20@motrum.ru"
        # to_email = "lars1515@yandex.ru"

        sending_result = send_email_message_html(subject, None, to_email, html_message=html_message)

        if data and sending_result:
            return Response("ok", status=status.HTTP_200_OK)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)