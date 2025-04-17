import math
import os
from unicodedata import category
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status
from django.db.models import Q, F, OrderBy, Case, When
from django.db.models import Prefetch

from apps.core.utils import (
    delete_everything_in_folder,
    get_file_path_add_more_doc,
    get_file_path_add_more_vac,
)
from apps.core.utils_web import (
    send_email_message_and_file,
    send_email_message_and_file_alternative,
)
from apps.logs.utils import error_alert
from apps.vacancy_web.api.serializers import VacancySerializer
from apps.vacancy_web.models import Vacancy, VacancyCategory
from project.settings import MEDIA_ROOT
import traceback


class VacancyViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Vacancy.objects.none()
    serializer_class = VacancySerializer
    http_method_names = ["get", "post"]

    @action(detail=False, url_path=r"load-ajax-vacancy-list")
    def load_ajax_vacancy_list(self, request, *args, **kwargs):
        if request.query_params.get("vacancy_category"):
            vacancy_category = request.query_params.get("vacancy_category")
            vacancy_category = vacancy_category.split(",")
            vacancy_category_get = VacancyCategory.objects.filter(
                slug__in=vacancy_category
            )

        else:
            vacancy_category = None

        print(vacancy_category)
        q_object = Q(is_actual=True)
        if vacancy_category is not None:
            q_object &= Q(vacancy_category__id__in=vacancy_category_get)
        print(q_object)
        queryset = (
            Vacancy.objects.filter(q_object)
            # .order_by("-data_project")[count : count + count_last]
        )
        print(queryset)
        serializer = VacancySerializer(
            queryset, context={"request": request}, many=True
        )
        data_response = {
            "data": serializer.data,
        }
        return Response(data=data_response, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path=r"send-vacancy")
    def send_vacancy(self, request, *args, **kwargs):
        from django.core.files.uploadedfile import InMemoryUploadedFile
        from django.core.files.storage import FileSystemStorage
        from django.template import loader

        try:
            data = request.data
            name = data["name"]
            phone = data["phone"]
            message = data["message"]
            file = data["file"]
            file_name = data["file"].name
            vacancy = data["vacancy"]

            if vacancy == "":
                vacancy = None

            images_last_list = file_name.split(".")
            type_file = "." + images_last_list[-1]

            new_dir, link, slugish = get_file_path_add_more_vac(
                None, type_file, file_name
            )
            doc_name = f"{slugish}{type_file}"
            f = FileSystemStorage(location=new_dir).save(doc_name, file)

            path_file = f"{MEDIA_ROOT}/{link}/{f}"

            if vacancy:
                subject = f"Отклик на вакансию {vacancy}{phone}"
            else:
                subject = f"Отклик без вакансии {name}{phone}"

            html_message = loader.render_to_string(
                "core/emails/email_vacancy.html",
                {
                    "client_name": name,
                    "client_phone": phone,
                    "text": message,
                    "vacancy": vacancy,
                },
            )

            to_manager = os.environ.get("EMAIL_HR")
            test = send_email_message_and_file_alternative(
                subject, None, to_manager, path_file, html_message
            )
            print("test-email", test)

            return Response(data=None, status=status.HTTP_200_OK)
        except Exception as e:

            tr = traceback.format_exc()
            error = "file_email_error"
            location = "Ошибка отправки вакансии "
            info = f"Ошибка отправки вакансии Тип ошибки:{e}{tr}"
            print(e)
            e = error_alert(error, location, info)

            return Response(data=None, status=status.HTTP_400_BAD_REQUEST)
