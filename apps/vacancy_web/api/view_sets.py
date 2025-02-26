import math
from unicodedata import category
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status
from django.db.models import Q, F, OrderBy, Case, When
from django.db.models import Prefetch

from apps.vacancy_web.api.serializers import VacancySerializer
from apps.vacancy_web.models import Vacancy, VacancyCategory



class VacancyViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Vacancy.objects.none()
    serializer_class = VacancySerializer
    http_method_names = [
        "get",
    ]
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
        q_object = Q()
        if vacancy_category is not None:
            q_object &= Q(vacancy_category__id__in=vacancy_category_get)
        print(q_object)
        queryset = (
            Vacancy.objects
            .filter(q_object)
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
