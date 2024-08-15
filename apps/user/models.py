from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, User, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import signals, Sum, Q
from django.dispatch import receiver


from apps.user.signals import update_group

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
    admin_type = models.CharField(max_length=100, choices=ADMIN_TYPE, default="ALL")
    
    class Meta:
        verbose_name = "Администратор"
        verbose_name_plural = "Администраторы"

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

        if self.admin_type == "ALL":
            self.is_superuser = True

        self.is_staff = True
        # if self.password is not None:
        #     self.set_password(self.password)

        super().save(*args, **kwargs)


signals.post_save.connect(update_group, sender=AdminUser)


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
        verbose_name ="Менеджер сайта"
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

