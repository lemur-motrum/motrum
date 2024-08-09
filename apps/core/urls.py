from django.urls import include, path

from . import views

# router.register(r'accounts', AccountViewSet)
app_name = 'core'

urlpatterns = [
    path("", views.index, name="index"),
    path("okt", views.okt, name="okt"),
    path("web", views.web, name="web"),

]
