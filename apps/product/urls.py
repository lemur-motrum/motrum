from django.urls import include, path

from apps.product.views import VendorAutocomplete, GropeAutocomplete,SupplierCategoryProductAllAutocomplete,SupplierCategoryProductAutocomplete,SupplierGroupProductAutocomplete
# from apps.product.views import  GropeAutocomplete

from . import views

from django.urls import re_path as url

app_name = 'product'

urlpatterns = [

    url(
        r"^vendor-autocomplete/$",
        VendorAutocomplete.as_view(),
        name="vendor-autocomplete",
    ),
    url(
        r"^group-autocomplete/$",
        GropeAutocomplete.as_view(),
        name="group-autocomplete",
    ),
    url(
        r"^category_supplier_all-autocomplete/$",
        SupplierCategoryProductAllAutocomplete.as_view(),
        name="category_supplier_all-autocomplete",
    ),
    url(
        r"^category_supplier-autocomplete/$",
        SupplierCategoryProductAutocomplete.as_view(),
        name="category_supplier-autocomplete",
    ),
    url(
        r"^group_supplier-autocomplete/$",
        SupplierGroupProductAutocomplete.as_view(),
        name="group_supplier-autocomplete",
    ),
     
]
