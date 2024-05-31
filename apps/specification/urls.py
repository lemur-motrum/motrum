from django.urls import include, path, re_path

from apps.product.models import Product

from . import views

from django.urls import re_path as url
from apps.specification.views import ProductAutocomplete, VendorAutocomplete

app_name = "specification"

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
]
