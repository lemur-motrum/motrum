from django.urls import include, path

from apps.specification.views import VendorAutocomplete


from . import views

from django.urls import re_path as url

app_name = 'product'

urlpatterns = [
    # path("", views.index, name="home"),
    url(
        r"^vendor-autocomplete/$",
        VendorAutocomplete.as_view(),
        name="vendor-autocomplete",
    ),

]
