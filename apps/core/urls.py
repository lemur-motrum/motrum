from django.urls import include, path
from . import views

# from .api import view_sets
from rest_framework import routers

# router.register(r'accounts', AccountViewSet)
app_name = "core"

router = routers.DefaultRouter()
# router.register(r"v1/email-callback", view_sets.ApiClient)

urlpatterns = [
    path("", views.index, name="index"),
    path("okt", views.okt, name="okt"),
    path("web", views.web, name="web"),
    path("personal_account/my_orders", views.my_orders, name="my_orders"),
    path("personal_account/my_documents", views.my_documents, name="my_documents"),
    path("personal_account/my_details", views.my_details, name="my_details"),
    path("personal_account/my_contacts", views.my_contacts, name="my_contacts"),
    path("send_email_callback", views.email_callback, name="send_email_callback"),
    path("send_email_manager", views.email_manager, name="send_email_manager"),
]
