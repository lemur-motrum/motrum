import traceback

from rest_framework import routers, serializers, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.client.models import Client
from apps.core.models import UpdatedCompanyBX24
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
    queryset = Notification.objects.all()
    serializer_class = None

    http_method_names = ["get", "post", "put"]
    
    
    @action(detail=False, methods=["post"], url_path=r"send-form-callback")
    def send_form_callback(self, request, *args, **kwargs):
        data = request.data
        data = {
            "name":"Имя",
            "phone":"телефон в формате 79999999999" 
        }
        if data:
            return Response("ok", status=status.HTTP_200_OK)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["post"], url_path=r"send-form-demo-visit")
    def send_form_demo_visit(self, request, *args, **kwargs):
        data = request.data
        # type = cobots-palett
        # cobots-box
        # cobots-packing
        # marking
        # shkaf-upravleniya

        data = {
            "type":"страница с которой демо выезд ",
            "name":"Имя",
            "phone":"телефон в формате 79999999999" 
        }
        if data:
            return Response("ok", status=status.HTTP_200_OK)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["post"], url_path=r"send-form-calculate-project")
    def send_form_calculate_project(self, request, *args, **kwargs):
        data = request.data
        data = {
            "name":"Имя",
            "phone":"телефон в формате 79999999999" 
        }
        if data:
            return Response("ok", status=status.HTTP_200_OK)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=False, methods=["post"], url_path=r"send-form-company-consultation")
    def send_form_company_consultation(self, request, *args, **kwargs):
        data = request.data
        data = {
            "name":"Имя",
            "phone":"телефон в формате 79999999999" 
        }
        if data:
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
        data = request.data
        data = {
           
            "name":"Имя",
            "phone":"телефон в формате 79999999999",
            "message":"Текст" 
        }
        if data:
            return Response("ok", status=status.HTTP_200_OK)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)