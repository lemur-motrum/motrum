from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
from .api import view_sets
from rest_framework import routers

app_name = 'client'


router = routers.DefaultRouter()
router.register(r"v1/client", view_sets.ApiClient)
# router.register(r"v1/requisites", view_sets.ApiRequisites)
# router.register(r"v1/account_requisites", view_sets.ApiAccountRequisites)
router.register(r"v1/client_requisites",view_sets.ApiClientRequisites)
# router.register(r"v1/client_info", view_sets.ApiAllClientRequisites)

urlpatterns = [
    path("", views.index, name="index"),
    # path("/<int:client_id>", views.client, name="lk"),

]
