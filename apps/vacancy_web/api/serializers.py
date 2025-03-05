from rest_framework import serializers

from apps.vacancy_web.models import Vacancy, VacancyPrice

# class VacancyPriceSerializer(serializers.ModelSerializer):


#     class Meta:
#         model = VacancyPrice
#         fields = (
#             "first",
#             "last",
#             "fixed",
#             "type_payments"
#         )


class VacancySerializer(serializers.ModelSerializer):

    # price = VacancyPriceSerializer(read_only=True, many=False)
    class Meta:
        model = Vacancy
        fields = "__all__"
