from django.urls import path

from . import views
from .api import view_sets
from rest_framework import routers

app_name = "projects_web"
router = routers.DefaultRouter()
router.register(r"v1/project", view_sets.ProjectViewSet)

urlpatterns = [
    path("", views.projects, name="projects"),  # проекты
    path("<slug:project>", views.project, name="project"),  # проект один
    path("", views.projects, name="projects"),  # проекты
]
