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

from .api.view_sets import ProductViewSet, CartViewSet
from django.views.generic import RedirectView
app_name = "product"

router = routers.DefaultRouter()
router.register(r"v1/product", ProductViewSet)
router.register(r"v1/cart", CartViewSet)

urlpatterns = [
    path("", views.catalog_all, name="catalog"),
    path("stock/",RedirectView.as_view(url='https://djangoproject.com')),
    
    
    path("<slug:category>", views.catalog_group, name="group"),
    path("<slug:category>/<slug:group>", views.products_items, name="products_items"),
    path(
        "<slug:category>/none_group/<slug:article>",
        views.product_one_without_group,
        name="product_one_without_group",
    ),
    path(
        "<slug:category>/<slug:group>/<slug:article>",
        views.product_one,
        name="product_one",
    ),
    path("add_document_admin/", views.add_document_admin, name="add_document_admin"),
    # url("product_ajax", views.catalog, name="catalog_ajax"),
    # АВТОЗАПОЛНЕНИЕ для бека
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
