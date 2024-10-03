from django.contrib.auth.models import Group, User, Permission


def upgrade_permission():

    s = Permission.objects.filter(
        content_type__app_label="product",
    )

    # codenames = ['view_blogpost', 'change_blogpost', 'add_blogpost', 	"delete_logentry"]
    from apps.user.models import ADMIN_TYPE

    for groupe_admin in ADMIN_TYPE:
        group = Group.objects.filter(name=groupe_admin[1]).first()
        if group.name == "Базовый доступ":
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
            permissions = Permission.objects.filter(codename__in=codenames)
           

            for permission in permissions.all():
                # group.permissions.clear()
                group.permissions.add(permission)

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
            ]
            permissions = Permission.objects.filter(codename__in=codenames)
        
            for permission in permissions.all():
                # group.permissions.clear()
                group.permissions.add(permission)

        elif group.name == "Доступ для загрузки каталогов поставщиков":
            pass
        elif group.name == "Полный доступ":
            pass
