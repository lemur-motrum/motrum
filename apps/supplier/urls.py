from django.urls import include, path


from . import views


app_name = 'supplier'

urlpatterns = [
    path("add_prompower", views.add_prompower, name="add_prompower"),
    # path("", views.index, name="home"),
     path("add_iek", views.add_iek, name="add_iek"),

]
