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
            QueryDict = {
                "event": ["ONCRMCOMPANYUPDATE"],
                "event_handler_id": ["110"],
                "data[FIELDS][ID]": ["17682"],
                "ts": ["1741082419"],
                "auth[domain]": ["pmn.bitrix24.ru"],
                "auth[client_endpoint]": ["https://pmn.bitrix24.ru/rest/"],
                "auth[server_endpoint]": ["https://oauth.bitrix.info/rest/"],
                "auth[member_id]": ["bd180ebaa3274830710fcdc4fd61de8f"],
                "auth[application_token]": ["a63ib122zuoyc5nuo69i8pkstp4mci52"],
            }
            companu = data.get("data[FIELDS][ID]")
            error = "file_api_error"
            location = "OK "
            info = f"{companu}OK {data}"
            for data_item in data:
                pass

            e = error_alert(error, location, info)
        except Exception as e:
            print(e)
            tr = traceback.format_exc()
            error = "file_api_error"
            location = "ERROR Исходящий вебхук изменение данных компании (менеджера))"
            info = (
                f"ERROR Исходящий вебхук изменение данных компании (менеджера)){e}{tr}"
            )
            e = error_alert(error, location, info)
