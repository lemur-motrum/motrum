from rest_framework import serializers

from apps.projects_web.models import (
    ClientCategoryProject,
    Project,
    ProjectClientCategoryProject,
    ProjectClientCategoryProjectMarking,
)


class ProjectClientCategoryProjectSerializer(serializers.ModelSerializer):
    client_category_name = serializers.SerializerMethodField()
    category_check = serializers.SerializerMethodField()

    class Meta:
        model = ProjectClientCategoryProject
        fields = "__all__"
        # exclude = ('requisites',)

    def get_client_category_name(self, obj):

        return obj.client_category.name

    def get_category_check(self, obj):
        if self.context["request"].query_params.get("client_category_project"):

            client_category_project_get = self.context["request"].query_params.get(
                "client_category_project"
            )
            client_category_project_get = client_category_project_get.split(",")

            if obj.client_category.slug in client_category_project_get:
                return True
            else:
                return False
            # print(1,client_category_project_get)


class ProjectClientCategoryProjectMarkingSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = ProjectClientCategoryProjectMarking
        fields = "__all__"

    def get_category_name(self, obj):
        return obj.client_category_marking.name


class ProjectSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    projectclientcategoryproject_set = ProjectClientCategoryProjectSerializer(
        read_only=False, many=True
    )
    projectclientcategoryprojectmarking_set = (
        ProjectClientCategoryProjectMarkingSerializer(read_only=False, many=True)
    )
    category_name = serializers.CharField(source="category_project", read_only=True)

    class Meta:
        model = Project
        fields = "__all__"

    def to_representation(self, instance):
        representation = super(ProjectSerializer, self).to_representation(instance)
        if representation["data_project"]:
            representation["data_project"] = instance.data_project.strftime("%Y")
        return representation
