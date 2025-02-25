from rest_framework import serializers

from apps.vacancy_web.models import Vacancy

class VacancySerializer(serializers.ModelSerializer):
    # url = serializers.CharField(source="get_absolute_url", read_only=True)
    # projectclientcategoryproject_set = ProjectClientCategoryProjectSerializer(
    #     read_only=False, many=True
    # )
    # projectclientcategoryprojectmarking_set = (
    #     ProjectClientCategoryProjectMarkingSerializer(read_only=False, many=True)
    # )
    # category_name = serializers.CharField(source="category_project", read_only=True)

    class Meta:
        model = Vacancy
        fields = "__all__"

    # def to_representation(self, instance):
    #     representation = super(ProjectSerializer, self).to_representation(instance)
    #     if representation["data_project"]:
    #         representation["data_project"] = instance.data_project.strftime("%Y")
    #     return representation