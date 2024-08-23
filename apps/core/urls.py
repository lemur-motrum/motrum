from django.urls import include, path
from . import views

# from .api import view_sets
from rest_framework import routers
from django.urls import re_path as url

# router.register(r'accounts', AccountViewSet)
app_name = "core"

router = routers.DefaultRouter()
# router.register(r"v1/email-callback", view_sets.ApiClient)

urlpatterns = [
    path("", views.index, name="index"),#главная
    path("okt", views.okt, name="okt"),#окт
    path("web", views.web, name="web"),#!!!удалить надо 
   
    path("company/", views.web, name="about"),#компания общая
    path("company/about", views.web, name="about"),#компания
    path("company/vacancy/", include("apps.vacancy_web.urls", namespace="vacancy")),
    #остальное по вакансии  в app vacancy_web
    path("solutions/", views.web, name="solutions"),#решения все
    path("marking", views.web, name="marking"),#решения маркировка
    path("cobots", views.web, name="cobots"),#решения коботы
    path("shkaf-upravleniya", views.web, name="shkaf-upravleniya"),#сборка шкафов управления
    path("contact", views.web, name="contact"),#контакты
    path("cart", views.cart, name="cart"),#корзина

    
    path("privacy-policy", views.web, name="privacy-policy"),#политика конфиденциальности
    # path("cart", views.cart,name="cart"),
    # path("/cart", include("apps.client.urls", namespace="cart")),
    #проекты в app project_web namespace="project"
    #каталог и товар  в app product
    #личный кабинет   в  app client  namespace="lk"
    
    # EMAILS
    
        # EMAILS
    path("send_email_callback", views.email_callback, name="send_email_callback"),
    path("send_email_manager", views.email_manager, name="send_email_manager"),
]
