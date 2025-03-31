from django.contrib import admin
from apps.core.models import PhotoEmoloeeInfoWeb
from apps.vacancy_web.models import (
    PhotoEducationInfoWeb,
    RequirementsVacancy,
    Responsibilities,
    Vacancy,
    VacancyCategory,
    VacancyPrice,
    WorkingConditions, PhotoSportsRecreationInfoWeb,
)
from project.admin import website_admin


# Register your models here.
# class WorkingConditionsInlineWeb(admin.TabularInline):
#     model = WorkingConditions
#     extra = 1


# class RequirementsVacancyInlineWeb(admin.TabularInline):
#     model = RequirementsVacancy
#     extra = 1


# class ResponsibilitiesInlineWeb(admin.TabularInline):
#     model = Responsibilities
#     extra = 1
class VacancyCategoryWebAdmin(admin.ModelAdmin):
    exclude = ["slug"]

    def has_delete_permission(self, request, obj=None):
        return False


# class VacancyPriceInlineWeb(admin.TabularInline):
#     model = VacancyPrice


class VacancyWebAdmin(admin.ModelAdmin):
    exclude = ["slug"]
    inlines = [
        #    VacancyPriceInlineWeb,
    ]
    list_display = [
        "name",
        "is_actual",
    ]

    def has_delete_permission(self, request, obj=None):
        return False


website_admin.register(Vacancy, VacancyWebAdmin)
website_admin.register(VacancyCategory, VacancyCategoryWebAdmin)
website_admin.register(PhotoEducationInfoWeb)
website_admin.register(PhotoSportsRecreationInfoWeb)
website_admin.register(PhotoEmoloeeInfoWeb)