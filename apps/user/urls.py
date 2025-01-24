from django.urls import include, path

from . import views

# router.register(r'accounts', AccountViewSet)
app_name = "user"

urlpatterns = [
    path("login_admin/", views.login_admin, name="login_admin"),
    path("logout_admin/", views.logout_admin, name="logout_admin"),
    path("login_admin_new", views.login_clear, name="login_admin_new"),
    path("logout_clear_info/", views.logout_clear_info, name="logout_clear_info"),
]
