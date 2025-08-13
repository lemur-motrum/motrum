from django.contrib.auth.models import Group, User, Permission
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


def upgrade_permission():

    s = Permission.objects.filter(
        content_type__app_label="product",
    )

    # codenames = ['view_blogpost', 'change_blogpost', 'add_blogpost', 	"delete_logentry"]
    from apps.user.models import ADMIN_TYPE

    for groupe_admin in ADMIN_TYPE:
        group = Group.objects.filter(name=groupe_admin[1]).first()
        if not group:
            continue
        elif group.name == "Базовый доступ":
            codenames = [
                "view_product",
                "view_price",
                "view_stock",
                "view_productimage",
                "view_productdocument",
                "change_price",
                "add_price",
                "add_specification",
                "view_specification",
                "add_productspecification",
                "view_productspecification",
            ]
            

        elif group.name == "Доступ администрирования товаров":
            codenames = [
                "view_product",
                "change_product",
                "add_product",
                "delete_product",
                "view_price",
                "change_price",
                "add_price",
                "delete_price",
                "view_stock",
                "change_stock",
                "add_stock",
                "delete_stock",
                "view_productproperty",
                "change_productproperty",
                "add_productproperty",
                "delete_productproperty",
                "view_productimage",
                "change_productimage",
                "add_productimage",
                "delete_productimage",
                "view_productdocument",
                "change_productdocument",
                "add_productdocument",
                "delete_productdocument",
                
                "view_discount",
                "view_supplier",
                "view_suppliercategoryproduct",
                "view_suppliercategoryproductall",
                "view_suppliergroupproduct",
                "view_vendor",
                "view_categoryproduct",
                "view_groupproduct",
                "view_logsaddproduct",
            ]
            

        elif group.name == "Доступ для загрузки каталогов поставщиков":
            continue
        elif group.name == "Полный доступ":
            continue
        else:
            continue
        
         # Получаем нужные разрешения
        permissions = Permission.objects.filter(codename__in=codenames)

        # Критически важно: очищаем старые права
        group.permissions.clear()

        # Добавляем новые
        group.permissions.add(*permissions)


def perform_some_action_on_login(sender, user,request, **kwargs):
    """
    A signal receiver which performs some actions for
    the user logging in.
    """
    ...
    # your code here
    current_user = request.user
    if current_user.is_staff:
        cookie = request.COOKIES.get("client_id")
        if cookie:
            print()
            # response = receiver(sender=sender)
            # response.set_cookie('client_id', domain="cookie_domain", max_age_seconds=1)
            # # response = django_logout(
            # #                     request,
            # #                     next_page=reverse("logout-confirmation")
            # #                 )
            
            # return response
            
