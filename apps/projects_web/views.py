from django.shortcuts import render

from apps.projects_web.models import CategoryProject, ClientCategoryProject, Project

# Create your views here.
# Create your views here.
def projects(request):
    projects = Project.objects.all()
    category_projects = CategoryProject.objects.all()
    client_category_projects = ClientCategoryProject.objects.all()
    

    context = {
        "projects":projects,
        "category_projects":category_projects,
        "client_category_projects":client_category_projects
        
        
    }
    return render(request, "projects_web/projects_all.html", context)

def project(request,project):
    project_one = Project.objects.get(slug=project)
    
    

    context = {
        "project":project_one
        
    }
    return render(request, "projects_web/project_one.html", context)