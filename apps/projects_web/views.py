from django.shortcuts import render
from django.db.models import Prefetch, OuterRef
from django.db.models import Q, F, OrderBy, Case, When, Value

from apps.projects_web.models import (
    CategoryProject,
    ClientCategoryProject,
    ClientCategoryProjectMarking,
    Project,
    ProjectClientCategoryProject,
    ProjectImage,
)


# Create your views here.
# Create your views here.
def projects(request):
    projects = Project.objects.all()
    category_projects = CategoryProject.objects.all()
    client_category_projects = ClientCategoryProject.objects.all()
    marking_category = ClientCategoryProjectMarking.objects.all()

    context = {
        "projects": projects,
        "category_projects": category_projects,
        "client_category_projects": client_category_projects,
        "marking_category": marking_category,
    }
    return render(request, "projects_web/projects_all.html", context)


def project(request, project):
    project_one = Project.objects.get(slug=project)
    project_image = ProjectImage.objects.filter(project=project_one)
    client_category_project = ProjectClientCategoryProject.objects.filter(
        project=project_one
    ).order_by("client_category__article")
    client_category_project_list = client_category_project.values("client_category")

    category_project_in_client = (
        ProjectClientCategoryProject.objects.filter(
            client_category__in=client_category_project_list
        )
        .distinct("project")
        .exclude(project=project_one)
        # .filter(
        #     project__category_project__slug__in=[
        #         "markirovka-chestnyij-znak",
        #         "robototehnicheskie-yachejki",
        #     ]
        # )
        .values_list("project")
    )
    project_in_client_category = Project.objects.filter(
        id__in=category_project_in_client
    ).filter(category_project__slug__in=["robototehnicheskie-yachejki","markirovka-chestnyij-znak",])

    print(category_project_in_client)
    if project_in_client_category.count() > 0:
        other_project = project_in_client_category
    else:
        other_project = None
        other_project = Project.objects.filter(
            category_project=project_one.category_project
        )

    print(other_project)
    context = {
        "project": project_one,
        "project_image": project_image,
        "client_category_project": client_category_project,
        "other_projects": other_project,
    }
    return render(request, "projects_web/project_one.html", context)
