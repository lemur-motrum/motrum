from django.db import models
from django.utils import timezone

from apps.product.models import Product
from apps.user.models import AdminUser

# Create your models here.

class LogsProductChange(models.Model):
    name = models.CharField("Название производителя", max_length=30)
    product = models.ForeignKey(
        Product,
        verbose_name="продукт",
        on_delete=models.PROTECT,
    )
    TYPE_LOGS = (
        ("changed", "Изменил"),
        ("null", "Нет значения"),
        ("error", "Ошибка при загрузке"),
      
    )
    type_logs = models.CharField(
        max_length=7, choices=TYPE_LOGS, default="null"
    )
    name_field = models.CharField("поле в модели в которой произошло событие лога", max_length=30)
    old_value =  models.CharField("старое значение", max_length=130)
    new_value =  models.CharField("новое значение", max_length=130)
    date = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    user = models.ForeignKey(
        AdminUser,
        verbose_name="администратор",
        on_delete=models.PROTECT,
    )
    class Meta:
        verbose_name = "Лог"
        verbose_name_plural = "Логи"

    def __str__(self):
        return self.name