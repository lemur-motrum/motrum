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
from apps.specification.views import CountryAutocomplete


urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),

    path('admin/', admin.site.urls),
    
    # url(r'^chaining/', include('smart_selects.urls')),
      
    path("", include("apps.core.urls", namespace="core")),
    path("client/", include("apps.client.urls", namespace="client")),
    path("logs/", include("apps.logs.urls", namespace="logs")),
    path("product/", include("apps.product.urls", namespace="product")),
    path("specification/", include("apps.specification.urls", namespace="specification")),
    path("supplier/", include("apps.supplier.urls", namespace="supplier")),
    path("user/", include("apps.user.urls", namespace="user")),
    path("admin_specification/", include("apps.admin_specification.urls", namespace="admin_specification")),
    
    
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
