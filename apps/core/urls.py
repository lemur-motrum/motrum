from django.urls import include, path

from apps import product
from . import views
from django.views.generic.base import TemplateView, RedirectView



from . import views
from .api import view_sets
from rest_framework import routers

app_name = "core"

router = routers.DefaultRouter()
router.register(r"v1/core", view_sets.Bitrix24ViewSet)
router.register(r"v1/core/forms", view_sets.FormWebViewSet)


urlpatterns = [
    path("", views.index, name="index"),  # главная
    path(
        "okt/",
        TemplateView.as_view(template_name="core/okt.html"),
        name="okt",
    ),  # окт
    path("company/", views.company, name="about"),  # компания общая
    path("company/about/", views.company_about, name="about_company"),  # компания
    path("company/vacancy/", include("apps.vacancy_web.urls", namespace="vacancy")),
    # остальное по вакансии  в app vacancy_web
    path("solutions/", views.solutions_all, name="solutions"),
    path("robots/", views.cobots_all, name="cobots"),
    path("cobots-palett/", views.solutions_one, name="cobots-palett"),
    path("cobots-box/", views.solutions_one, name="cobots-box"),
    path("cobots-packing/", views.solutions_one, name="cobots-packing"),
    path("marking/", views.solutions_one, name="marking"),
    path("shkaf-upravleniya/", views.solutions_one, name="shkaf-upravleniya"),
    path(
        "contact/",
        views.contact_page,
        name="contact",
    ),  # контакты
    path("cart/", views.cart, name="cart"),  # корзина
    path(
        "privacy-policy/", views.privacy_policy, name="privacy-policy"
    ),  # политика конфиденциальности
    path("brand/", product.views.brand_all, name="brand"),
    path("brand/<slug:vendor>/", product.views.brand_one, name="brand_one"),
    path("add_admin_okt/", views.add_admin_okt, name="add_admin_okt"),
    path(
        "company/detributer-certificate/",
        views.certificates_page,
        name="detributer-certificate",
    ),
    path(
        "company/certificate-of-conformity/",
        views.certificates_page,
        name="certificate-of-conformity",
    ),
    path(
        "company/sout/",
        views.certificates_page,
        name="sout",
    ),
    path("robots.txt", views.robots_txt, name="robots_txt",),
    
    path("stock/", RedirectView.as_view(url='/product/', permanent=True)),
    path("cobots/", RedirectView.as_view(url='/cobots-palett/', permanent=True)),
    path("product/view/63/", RedirectView.as_view(url='/brand/veda/?vendor=veda&page=1', permanent=True)),
    path("product/view/56/", RedirectView.as_view(url='/brand/emas/?vendor=emas&page=1', permanent=True)),
    path("product/view/57/", RedirectView.as_view(url='/brand/oni/?vendor=oni&page=1', permanent=True)),
    path("product/view/58/", RedirectView.as_view(url='/brand/unimat/?vendor=unimat&page=1', permanent=True)),
    path("product/view/59/", RedirectView.as_view(url='/brand/skb-induktsiya/?vendor=skb-induktsiya&page=1', permanent=True)),
    path("product/view/60/", RedirectView.as_view(url='/brand/prompower/?vendor=prompower&page=1', permanent=True)),
    path("product/view/61/", RedirectView.as_view(url='/brand/omron/?vendor=omron&page=1', permanent=True)),
    path("product/view/62/", RedirectView.as_view(url='/brand/tbloc/?vendor=tbloc&page=1', permanent=True)),
    path("news/view/44/", RedirectView.as_view(url='/company/sout/', permanent=True)),
    # path(
    #     "robots.txt",
    #     TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    # ),
    
    
    
]
