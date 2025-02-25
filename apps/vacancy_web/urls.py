from django.urls import path

from . import views
from .api import view_sets
from rest_framework import routers

app_name = "vacancy_web"
router = routers.DefaultRouter()
router.register(r"v1/vacancy", view_sets.VacancyViewSet)

urlpatterns = [
    path("", views.vacancy, name="vacancy"),
    path("<slug:slug>/", views.vacancy_item, name="vacancy_item"),
]
