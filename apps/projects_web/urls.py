from django.urls import path

from . import views

app_name = "projects_web"

urlpatterns = [
    path("", views.projects, name="projects"),#проекты
    path("<slug:project>", views.project, name="project"),#проект один
    
]