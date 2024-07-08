from django.urls import include, path

from django.urls import re_path as url
from . import views


app_name = "admin_specification"


urlpatterns = [
    path("", views.specifications, name="specifications"),
    path("specification/", views.create_specification, name="create_specification"),
    path(
        "save_specification_view_admin/",
        views.save_specification_view_admin,
        name="save_specification_view_admin",
    ),
]
