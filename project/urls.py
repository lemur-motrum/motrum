"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.urls import re_path as url

from project.admin import website_admin
from rest_framework import routers

from apps.client.urls import router as client_router
from apps.product.urls import router as product_router
from apps.notifications.urls import router as notifications_router
from apps.projects_web.urls import router as projects_web_router

from django.contrib.staticfiles.urls import staticfiles_urlpatterns



router = routers.DefaultRouter()
router.registry.extend(client_router.registry)
router.registry.extend(product_router.registry)
router.registry.extend(notifications_router.registry)
router.registry.extend(projects_web_router.registry)


urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),

    path('admin/', admin.site.urls),
    # path('admin/', include("apps.user.urls", namespace="user")),
    path('website_admin/', website_admin.urls),
   
    path("", include("apps.core.urls", namespace="core")),
    path("lk/", include("apps.client.urls", namespace="lk")),
    path("logs/", include("apps.logs.urls", namespace="logs")),
    path("product/", include("apps.product.urls", namespace="product")),
    path("specification/", include("apps.specification.urls", namespace="specification")),
    path("supplier/", include("apps.supplier.urls", namespace="supplier")),
    path("user/", include("apps.user.urls", namespace="user")),
    path("admin_specification/", include("apps.admin_specification.urls", namespace="admin_specification")),
    
    # для сайта
    path("project/", include("apps.projects_web.urls", namespace="project")),
    # path("vacancy/", include("apps.vacancy_web.urls", namespace="vacancy")),
    
    # апи
    path("api/", include(router.urls)),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# else:
#     urlpatterns += staticfiles_urlpatterns()

handler403 = "apps.core.views.permission_denied"
handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"