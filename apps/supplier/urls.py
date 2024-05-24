from django.urls import include, path


from . import views


app_name = 'supplier'

urlpatterns = [
    path("add_prompower", views.add_prompower, name="add_prompower"),
    # path("", views.index, name="home"),
    path("add_iek", views.add_iek, name="add_iek"),
    path("get_currency_api", views.get_currency_api, name="get_currency_api"),
    path("get_currency_file", views.get_currency_file, name="get_currency_file"),
]