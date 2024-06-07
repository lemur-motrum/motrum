from django.db import models
from django.utils import timezone

from apps.product.models import Product
from apps.user.models import AdminUser


# Create your models here.
TYPE_LOGS_ERROR = (
    ("file_structure_error", "фаил не соответствует нужной структуре"),
    ("file_api_error", "фаил не соответствует нужной структуре"),
    ("error", "Ошибка"),
)


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
    type_logs = models.CharField(max_length=7, choices=TYPE_LOGS, default="null")
    name_field = models.CharField(
        "поле в модели в которой произошло событие лога", max_length=30
    )
    old_value = models.CharField("старое значение", max_length=130)
    new_value = models.CharField("новое значение", max_length=130)
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


class LogsError(models.Model):

    date = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    type_error = models.CharField(
        max_length=20, choices=TYPE_LOGS_ERROR, default="error"
    )
    location = models.CharField(
        "место ошибки",
        max_length=200,
        blank=True,
        null=True,
    )
    info = models.CharField(
        "инфо о ошибкe",
        max_length=200,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Лог ошибок"
        verbose_name_plural = "Логи ошибок"

    def __str__(self):
        return f"Тип ошибки: {self.type_error},{self.date} "
