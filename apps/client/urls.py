from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
from .api import view_sets
from rest_framework import routers

app_name = "client"


router = routers.DefaultRouter()
router.register(r"v1/client", view_sets.ClientViewSet)
router.register(r"v1/client-requisites",view_sets.ClientRequisitesAccountViewSet, basename="client-requisites")
router.register(r"v1/requisites",view_sets.RequisitesViewSet)
router.register(r"v1/order",view_sets.OrderViewSet)




urlpatterns = [
    path("", views.index, name="index"),
    path("my_orders", views.my_orders, name="my_orders"),
    path("my_documents", views.my_documents, name="my_documents"),
    path("my_details", views.my_details, name="my_details"),
    path("my_contacts", views.my_contacts, name="my_contacts"),
]
