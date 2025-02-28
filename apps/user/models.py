from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, User, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import signals, Sum, Q
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from apps.core.utils_web import get_file_path_company_web
from apps.user.signals import update_group, user_admin_logged_in
from apps.user.utils import perform_some_action_on_login

# Create your models here.
ADMIN_TYPE = (
    ("BASE", "Базовый доступ"),
    ("PRODUCT", "Доступ администрирования товаров"),
    ("CATALOG", "Доступ для загрузки каталогов поставщиков"),
    ("ALL", "Полный доступ"),
)


class CustomUser(AbstractUser):
    pass


# юзер администратор
class AdminUser(CustomUser):
    user = models.OneToOneField(CustomUser, parent_link=True, on_delete=models.CASCADE)
    middle_name = models.CharField("Отчество", max_length=50, null=True, blank=True)
    admin_type = models.CharField("Уровень доступа",max_length=100, choices=ADMIN_TYPE, default="ALL")
    bitrix_id = models.PositiveIntegerField(
        "Номер менеджера битрикс",
        null=True,
        blank=True,
    )
    image = models.ImageField(
        "Картинка",
        upload_to=get_file_path_company_web,
        max_length=500,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Администратор"
        verbose_name_plural = "Администраторы"

    def save(self, *args, **kwargs):
        all_user =  AdminUser.objects.all()
        if all_user.count() > 0:
            if self.id:
                user = AdminUser.objects.get(id=self.id)
                password_old = user.password
                if password_old == self.password:
                    pass
                else:
                    self.set_password(self.password)
            else:
                self.set_password(self.password)

            if self.admin_type == "ALL":
                self.is_superuser = True

            self.is_staff = True
            # if self.password is not None:
            #     self.set_password(self.password)
        else:
            pass
        super().save(*args, **kwargs)

    # def login_bitrix(self,data):
    #     pass

    @classmethod
    def login_bitrix(cls, data, next_url, request):
        print(data)
        try:
            admin = cls.objects.get(username=data["email_bitrix_manager"], password=data["token"])
            is_groups_user = admin.groups.filter(
                name__in=["Полный доступ", "Базовый доступ"]
            ).exists()

            if admin.is_active and is_groups_user:
                login(request, admin)
                if next_url:
                    pass
                    response = redirect(next_url)
                    response.set_cookie("client_id", max_age=-1)
                    response.set_cookie("cart", max_age=-1)
                    response.set_cookie("specificationId", max_age=-1)
                    return redirects
                else:
                    data = {
                        "status_admin": 200,
                        "admin": admin,
                    }
                    return data

            else:
                data = {"status_admin": 403}
            return data
        except cls.DoesNotExist:
            data = {"status_admin": 401}
            return data


signals.post_save.connect(update_group, sender=AdminUser)
user_logged_in.connect(
    perform_some_action_on_login,
)


class Roles(Group):
    class Meta:
        proxy = True
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


#         7.1. Базовый доступ
# Позволяет просматривать каталог товаров и собирать спецификации.

# 7.2. Доступ администрирования товаров
# Позволяет добавлять, удалять и редактировать товары в ОКТ.

# 7.3. Доступ для загрузки каталогов поставщиков
# Позволяет производить загрузки обновлений каталогов от поставщиков.

# 7.4. Полный доступ
# Позволяет просматривать историю изменений и предоставлять права доступа и корректировать условия скидок поставщиков.


class ManagerWebUser(CustomUser):
    user = models.OneToOneField(CustomUser, parent_link=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Менеджер сайта"
        verbose_name_plural = "Менеджер сайта"

    def save(self, *args, **kwargs):
        if self.id:
            user = AdminUser.objects.get(id=self.id)
            password_old = user.password
            if password_old == self.password:
                pass
            else:
                self.set_password(self.password)
        else:
            self.set_password(self.password)

        self.is_staff = True

        super().save(*args, **kwargs)
