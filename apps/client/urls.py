from django.urls import include, path
from django.views.generic.base import TemplateView

from . import views
from .api import view_sets
from rest_framework import routers

app_name = "client"


router = routers.DefaultRouter()
router.register(r"v1/client", view_sets.ClientViewSet)
router.register(
    r"v1/client-requisites",
    view_sets.ClientRequisitesAccountViewSet,
    basename="client-requisites",
)
router.register(r"v1/requisites", view_sets.RequisitesViewSet)
router.register(r"v1/accountreq", view_sets.AccountRequisitesViewSet)
router.register(r"v1/adress_requisites", view_sets.RequisitesAddressViewSet)
router.register(r"v1/order", view_sets.OrderViewSet)
router.register(r"v1/emails", view_sets.EmailsViewSet)


urlpatterns = [
    path("", views.index, name="index"),
    path("my_orders/", views.my_orders, name="my_orders"),
    path("my_documents/", views.my_documents, name="my_documents"),
    path("my_details/", views.my_details, name="my_details"),
    path("my_contacts/", views.my_contacts, name="my_contacts"),
    path("user_logout/", views.user_logout, name="user_logout"),
    path("order/<int:pk>/", views.order_client_one, name="order_client_one"),
    
    # URL для конвертации XLSX в PDF
    path("convert-xlsx-to-pdf/<path:xlsx_path>/", views.convert_xlsx_to_pdf_view, name="convert_xlsx_to_pdf"),
    path("bill-conversion/<int:order_id>/", views.BillConversionView.as_view(), name="bill_conversion"),
]
