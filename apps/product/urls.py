from django.urls import include, path

from apps.product.views import VendorAutocomplete, GropeAutocomplete,CategSupAutocomplete
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
        r"^catesup-autocomplete/$",
        CategSupAutocomplete.as_view(),
        name="catesup-autocomplete",
    ),
     
]
