from django.urls import include, path

from django.urls import re_path as url
from . import views


app_name = 'admin_specification'


urlpatterns = [
    path("specifications", views.specifications, name="specifications"),
    # path("specification_add", views.specification_add, name="specification_add"),
    # path("specification_catalog", views.specification_catalog, name="specification_catalog"),

]