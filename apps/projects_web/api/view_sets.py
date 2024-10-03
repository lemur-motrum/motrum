from unicodedata import category
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status
from django.db.models import Q, F, OrderBy

from apps.projects_web.api.serializers import ProjectSerializer
from apps.projects_web.models import Project


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Project.objects.none()
    serializer_class = ProjectSerializer
    http_method_names = [
        "get",
    ]

    @action(detail=False, url_path=r"load-ajax-project-list")
    def load_ajax_match_list(self, request, *args, **kwargs):
        count = int(request.query_params.get("count"))
        count_last = 10
        print(request.query_params)

        if request.query_params.get("category_project"):
            category_project_get = request.query_params.get("category_project")
        else:
            category_project_get = None

        if request.query_params.get("client_category_project"):
            client_category_project_get = request.query_params.get(
                "client_category_project"
            )
        else:
            client_category_project_get = None

        q_object = Q()
        if category_project_get is not None:
            q_object &= Q(category_project__slug=category_project_get)
        if client_category_project_get is not None:
            q_object &= Q(client_category_project__slug=client_category_project_get)

        queryset = Project.objects.select_related(
            "category_project",
            "client_category_project",
        ).filter(q_object)[count : count + count_last]

        serializer = ProjectSerializer(
            queryset, context={"request": request}, many=True
        )
        data_response = {
            "data": serializer.data,
        }
        return Response(data=data_response, status=status.HTTP_200_OK)
