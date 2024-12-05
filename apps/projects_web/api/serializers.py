from rest_framework import serializers

from apps.projects_web.models import ClientCategoryProject, Project, ProjectClientCategoryProject

class ProjectClientCategoryProjectSerializer(serializers.ModelSerializer):
    client_category_name = serializers.SerializerMethodField()
    class Meta:
        model = ProjectClientCategoryProject
        fields = "__all__"
        # exclude = ('requisites',)
    
    def get_client_category_name(self, obj):

        return obj.client_category.name

        
        
class ProjectSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    projectclientcategoryproject_set = ProjectClientCategoryProjectSerializer(read_only=False, many=True)
    class Meta:
        model = Project
        fields = "__all__"

    def to_representation(self, instance):
        representation = super(ProjectSerializer, self).to_representation(instance)
        if representation["data_project"]:
            representation["data_project"] = instance.data_project.strftime(
                "%Y"
            )
          
        return representation
