from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models

from apps.projects_web.models import (
    CategoryProject,
    ClientCategoryProject,
    ClientCategoryProjectMarking,
    Project,
    ProjectClientCategoryProject,
    ProjectClientCategoryProjectMarking,
    ProjectImage,
    ProjectTextBlock,
    ProjectVideo,
)
from project.admin import website_admin


# Register your models here.
class ProjectImageInlineWeb(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image",)
    
class ProjectVideoInlineWeb(admin.TabularInline):
    model = ProjectVideo
    extra = 1
    fields = ("video",)
    
class ProjectTextBlockWeb(admin.TabularInline):
    model = ProjectTextBlock
    extra = 3
    # fields = ("title","short_text","text")
    fieldsets = [
        (
            None,
            {
                "fields": [
                    ("title"),
                    ("text"),
                    
                ]
            },
        )
    ]
    

    
class ProjectClientCategoryProjectInlineWeb(admin.TabularInline):
    model = ProjectClientCategoryProject
    extra = 1
    fields = ("client_category",)
    
class ProjectClientCategoryProjectMarkingeWeb(admin.TabularInline):
    model = ProjectClientCategoryProjectMarking
    extra = 1
    fields = ("client_category_marking",)    

class ProjectWebAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "is_view_home_web",
    ]
    exclude = ["slug","data_create"]
    fieldsets = [
        (
            "Основные параметры",
            {
                "fields": [
                    "is_view_home_web",
                    "image_main",
                    "name",
                    "text",
                    ("data_project","place_object"),
                    "category_project",

                ],
            },
        ),
    ]
    inlines = [
        ProjectClientCategoryProjectInlineWeb,
        ProjectClientCategoryProjectMarkingeWeb,
        ProjectImageInlineWeb,
        ProjectVideoInlineWeb,
        ProjectTextBlockWeb,
        
    ]
    # def has_delete_permission(self, request,obj=None):
    #     return False


class CategoryProjectWebAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "article",
    ]
    exclude = ["slug"]
    def has_delete_permission(self, request,obj=None):
        return False

class ClientCategoryProjectMarkingAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "article",
    ]
    exclude = ["slug"]
    
    def has_delete_permission(self, request,obj=None):
        return False    


class ClientCategoryProjectWebAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "article",
    ]
    exclude = ["slug"]
    def has_delete_permission(self, request,obj=None):
        return False


website_admin.register(Project, ProjectWebAdmin)
website_admin.register(CategoryProject, CategoryProjectWebAdmin)
website_admin.register(ClientCategoryProject, ClientCategoryProjectWebAdmin)
website_admin.register(ClientCategoryProjectMarking, ClientCategoryProjectMarkingAdmin)
