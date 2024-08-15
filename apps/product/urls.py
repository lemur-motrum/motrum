from django.urls import include, path

from rest_framework import routers

from apps.product.views import (
    VendorAutocomplete,
    GropeAutocomplete,
    SupplierCategoryProductAllAutocomplete,
    SupplierCategoryProductAutocomplete,
    SupplierGroupProductAutocomplete,
)

# from apps.product.views import  GropeAutocomplete

from . import views
from .api import view_sets
from rest_framework import routers

from django.urls import re_path as url

from .api.view_sets import ProductViewSet

app_name = "product"

router = routers.DefaultRouter()
router.register(r"v1/product", ProductViewSet)
router.register(
    r"v1/product-test", view_sets.ApiCProductViewSet, basename="product-test"
)

urlpatterns = [
    url("", views.catalog, name="catalog"),
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
