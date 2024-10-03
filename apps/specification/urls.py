from django.urls import include, path, re_path

from apps.product.models import Product
from apps.specification.api.view_sets import SpecificationViewSet
from apps.specification.models import ProductSpecification
from project import admin
from .api import view_sets
from rest_framework import routers

from django.urls import re_path as url

from . import views

from django.urls import re_path as url
from apps.specification.views import (
    ProductAutocomplete,
    PriceOneAutocomplete,
    VendorAutocomplete,
)

app_name = "specification"

router = routers.DefaultRouter()
router.register(r"v1/specification", SpecificationViewSet)

urlpatterns = [
    url(
        r"^product-autocomplete/$",
        ProductAutocomplete.as_view(),
        name="product-autocomplete",
    ),
    url(
        r"^vendor-autocomplete/$",
        VendorAutocomplete.as_view(),
        name="vendor-autocomplete",
    ),
    url(
        r"^price-one-autocomplete/$",
        PriceOneAutocomplete.as_view(
            model=ProductSpecification,
            create_field="price_one",
            validate_create=True,
        ),
        name="price-one-autocomplete",
    ),
]
