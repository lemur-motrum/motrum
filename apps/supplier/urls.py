from django.urls import include, path

from .views import (
    SupplierCategoryAutocomplete,
    SupplierGroupAutocomplete,
    VendorAutocomplete,
    SupplierCategoryProductAllAutocomplete,
    GroupProductAutocomplete,
)

from django.urls import re_path as url
from . import views


app_name = "supplier"

urlpatterns = [
    path("add_iek", views.add_iek, name="add_iek"),
    path("test", views.test, name="test"),
    path(
        "save_emas_props", views.save_emas_props, name="save_emas_props"
    ),  # характеристики и фото есмас из выгрузок первичное
    path("add_permission", views.add_permission, name="add_permission"),  # Праздники
    path("add_holidays", views.add_holidays, name="add_holidays"),  # права админа
    path("get_currency", views.get_currency, name="get_currency"),
    path("add_stage_bx", views.add_stage_bx, name="add_stage_bx"),
    # url для автозаполнения
    url(
        r"^vendor-autocomplete/$",
        VendorAutocomplete.as_view(),
        name="vendor-autocomplete",
    ),
    url(
        r"^category-autocomplete/$",
        SupplierCategoryAutocomplete.as_view(),
        name="category-autocomplete",
    ),
    url(
        r"^group-autocomplete/$",
        SupplierGroupAutocomplete.as_view(),
        name="group-autocomplete",
    ),
    url(
        r"^category-all-autocomplete/$",
        SupplierCategoryProductAllAutocomplete.as_view(),
        name="category-all-autocomplete",
    ),
    url(
        r"^group_catalog-autocomplete/$",
        GroupProductAutocomplete.as_view(),
        name="group_catalog-autocomplete",
    ),
]
