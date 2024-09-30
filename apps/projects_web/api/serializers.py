from rest_framework import serializers

from apps.projects_web.models import Project

class ProjectSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    
    class Meta:
        model = Project
        fields = "__all__"