from django.urls import include, path
from . import views
from django.views.generic.base import TemplateView

# from .api import view_sets
from rest_framework import routers
from django.urls import re_path as url

# router.register(r'accounts', AccountViewSet)
app_name = "core"

router = routers.DefaultRouter()
# router.register(r"v1/email-callback", view_sets.ApiClient)

urlpatterns = [
    path("", views.index, name="index"),  # главная
    path(
        "okt/",
        TemplateView.as_view(template_name="core/okt.html"),
        name="okt",
    ), # окт

    path("company/", views.index, name="about"),  # компания общая
    path("company/about", views.index, name="about_company"),  # компания
    path("company/vacancy/", include("apps.vacancy_web.urls", namespace="vacancy")),
    # остальное по вакансии  в app vacancy_web
    path(
        "solutions/",
        TemplateView.as_view(template_name="core/solutions/solutions_all.html"),
        name="solutions",
    ),  # решения все
    path(
        "marking/",
        TemplateView.as_view(template_name="core/solutions/marking.html"),
        name="marking",
    ),  # решения маркировка
    path(
        "cobots/",
        TemplateView.as_view(template_name="core/solutions/cobots.html"),
        name="cobots",
    ),  # решения коботы
    path(
        "shkaf-upravleniya/",
        TemplateView.as_view(template_name="core/solutions/shkaf-upravleniya.html"),
        name="shkaf-upravleniya",
    ),  # сборка шкафов управления
    path("contact", views.index, name="contact"),  # контакты
    path("cart", views.cart, name="cart"),  # корзина
    path(
        "privacy-policy", views.privacy_policy, name="privacy-policy"
    ),  # политика конфиденциальности
    # path("cart", views.cart,name="cart"),
    # path("/cart", include("apps.client.urls", namespace="cart")),
    # проекты в app project_web namespace="project"
    # каталог и товар  в app product
    # личный кабинет   в  app client  namespace="lk"
    # EMAILS
    # EMAILS
    path("send_email_callback", views.email_callback, name="send_email_callback"),
    path("send_email_manager", views.email_manager, name="send_email_manager"),
]
