from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    pass

class AdminUser(CustomUser):
  
    user = models.OneToOneField(
        CustomUser, parent_link=True, on_delete=models.CASCADE
    )
    middle_name = models.CharField("Отчество", max_length=20, blank=True)


    class Meta:
        verbose_name = "Администратор"
        verbose_name_plural = "Администраторы"
        
        
#         7.1. Базовый доступ
# Позволяет просматривать каталог товаров и собирать спецификации. 

# 7.2. Доступ администрирования товаров
# Позволяет добавлять, удалять и редактировать товары в ОКТ.

# 7.3. Доступ для загрузки каталогов поставщиков
# Позволяет производить загрузки обновлений каталогов от поставщиков.

# 7.4. Полный доступ
# Позволяет просматривать историю изменений и предоставлять права доступа и корректировать условия скидок поставщиков.