from django.urls import path

from . import views


app_name = "admin_specification"


urlpatterns = [
    path("", views.all_categories, name="categories"),
    path("products/<int:cat>", views.group_product, name="groups"),
    path("product/<int:cat>", views.instruments, name="instruments"),
    path("products/<int:cat>/<int:gr>", views.specifications, name="specifications"),
    path(
        "current_specification/",
        views.create_specification,
        name="create_specification",
    ),
    path(
        "all_specifications/", views.get_all_specifications, name="all_specifications"
    ),
    path(
        "save_specification_view_admin/",
        views.save_specification_view_admin,
        name="save_specification_view_admin",
    ),
    path("search_product/", views.search_product, name="search_product"),
    path("load_products/", views.load_products, name="load_products"),
    path(
        "update_specification/", views.update_specification, name="update_specification"
    ),
]
