from django.contrib import admin
from apps.vacancy_web.models import (
    RequirementsVacancy,
    Responsibilities,
    Vacancy,
    WorkingConditions,
)
from project.admin import website_admin


# Register your models here.
class WorkingConditionsInlineWeb(admin.TabularInline):
    model = WorkingConditions
    extra = 1


class RequirementsVacancyInlineWeb(admin.TabularInline):
    model = RequirementsVacancy
    extra = 1


class ResponsibilitiesInlineWeb(admin.TabularInline):
    model = Responsibilities
    extra = 1


class VacancyWebAdmin(admin.ModelAdmin):
    exclude = ["slug"]
    inlines = [
        WorkingConditionsInlineWeb,
        RequirementsVacancyInlineWeb,
        ResponsibilitiesInlineWeb,
    ]
    list_display = [
        "name",
        "is_actual",
    ]


website_admin.register(Vacancy, VacancyWebAdmin)
