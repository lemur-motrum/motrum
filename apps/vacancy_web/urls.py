from django.urls import path

from . import views

app_name = "vacancy_web"

urlpatterns = [
    path("", views.vacancy, name="vacancy"),
    path("<slug:slug>/", views.vacancy_item, name="vacancy_item"),
]
