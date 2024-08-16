from django.urls import path

from . import views

app_name = "projects_web"

urlpatterns = [
    path("", views.index, name="projects"),#проекты
    
]