from django.urls import include, path

from .views import  SupplierCategoryAutocomplete, SupplierGroupAutocomplete, VendorAutocomplete,SupplierCategoryProductAllAutocomplete,GroupProductAutocomplete

from django.urls import re_path as url
from . import views


app_name = 'supplier'

urlpatterns = [
    path("add_prompower", views.add_prompower, name="add_prompower"),
    # path("", views.index, name="home"),
    path("add_iek", views.add_iek, name="add_iek"),
    path("get_currency_api", views.get_currency_api, name="get_currency_api"),
    path("get_currency_file", views.get_currency_file, name="get_currency_file"),
    path("test", views.test, name="test"),

    path("add_permission", views.add_permission, name="add_permission"),# права админа
    
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