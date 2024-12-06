import math
from unicodedata import category
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status
from django.db.models import Q, F, OrderBy, Case, When
from django.db.models import Prefetch

from apps.projects_web.api.serializers import ProjectSerializer
from apps.projects_web.models import (
    Project,
    ProjectClientCategoryProject,
    ProjectClientCategoryProjectMarking,
)


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Project.objects.none()
    serializer_class = ProjectSerializer
    http_method_names = [
        "get",
    ]

    @action(detail=False, url_path=r"load-ajax-project-list")
    def load_ajax_project_list(self, request, *args, **kwargs):
        count = int(request.query_params.get("count"))
        count_last = 10

        if request.query_params.get("category_project"):
            category_project_get = request.query_params.get("category_project")
        else:
            category_project_get = None

        if request.query_params.get("client_category_project"):
            client_category_project_get = request.query_params.get(
                "client_category_project"
            )
            client_category_project_get = client_category_project_get.split(",")
            client_category = ProjectClientCategoryProject.objects.filter(
                client_category__slug__in=client_category_project_get
            ).distinct("project")
        else:
            client_category_project_get = None

        if request.query_params.get("category_project_marking"):
            category_project_marking_get = request.query_params.get(
                "category_project_marking"
            )
            category_project_marking_get = category_project_marking_get.split(",")
            category_marking = ProjectClientCategoryProjectMarking.objects.filter(
                client_category_marking__slug__in=category_project_marking_get
            ).distinct("project")
        else:
            category_project_marking_get = None

        q_object = Q()
        if category_project_get is not None:
            q_object &= Q(category_project__slug=category_project_get)
        if client_category_project_get is not None:
            q_object &= Q(projectclientcategoryproject__id__in=client_category)

        if category_project_marking_get is not None:
            q_object &= Q(projectclientcategoryprojectmarking__id__in=category_marking)

        queryset = (
            Project.objects.select_related("category_project")
            .prefetch_related(
                Prefetch("projectclientcategoryproject_set"),
                Prefetch("projectclientcategoryproject_set__client_category"),
                Prefetch("projectclientcategoryprojectmarking_set"),
                Prefetch("projectclientcategoryprojectmarking_set__client_category_marking"),
                )
            .filter(q_object).order_by("-data_project")[count : count + count_last]
        )
        queryset_next = Project.objects.filter(q_object).order_by("-data_project")[
            count + count_last : count + count_last + 1
        ].exists()

        serializer = ProjectSerializer(
            queryset, context={"request": request}, many=True
        )

        data_response = {
            "data": serializer.data,
            "next": queryset_next,
            
        }
        return Response(data=data_response, status=status.HTTP_200_OK)
