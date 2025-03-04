import traceback

from rest_framework import routers, serializers, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.client.models import Client
from apps.logs.utils import error_alert

class Bitrix24ViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = None

    http_method_names = ["get", "post", "put"]
    
    @action(detail=False, methods=["post"], url_path=r"client-b24")
    def client_b24(self, request, *args, **kwargs):
        try:
            data = request.data
            event = request.event
            print(data)
            error = "file_api_error"
            location = "OK "
            info = f"OK {event}{data}"
            e = error_alert(error, location, info)
        except Exception as e:
            print(e)
            tr = traceback.format_exc()
            error = "file_api_error"
            location = "ERROR Исходящий вебхук изменение данных компании (менеджера))"
            info = f"ERROR Исходящий вебхук изменение данных компании (менеджера)){e}{tr}"
            e = error_alert(error, location, info)