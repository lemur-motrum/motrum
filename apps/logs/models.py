from django.db import models
from django.utils import timezone

from apps.product.models import Product
from apps.user.models import AdminUser


# Create your models here.
TYPE_LOGS_ERROR = (
    ("file_structure_error", "фаил не соответствует нужной структуре"),
    ("file_api_error", "ошибка при загрузке с api"),
    ("error", "Ошибка"),
    
)


class LogsProductChange(models.Model):
    TYPE_LOGS = (
        ("changed", "Изменил"),
        ("null", "Нет значения"),
        ("error", "Ошибка при загрузке"),
    )
    name = models.CharField("Название производителя", max_length=30)
    product = models.ForeignKey(
        Product,
        verbose_name="Продукт",
        on_delete=models.PROTECT,
    )
    type_logs = models.CharField(max_length=7, choices=TYPE_LOGS, default="null")
    name_field = models.CharField(
        "Поле в модели в которой произошло событие лога", max_length=30
    )
    old_value = models.CharField("Старое значение", max_length=130)
    new_value = models.CharField("Новое значение", max_length=130)
    date = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    created_timestamp = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления"
                                             )
    user = models.ForeignKey(
        AdminUser,
        verbose_name="Администратор",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "Лог"
        verbose_name_plural = "Логи"

    def __str__(self):
        return self.name


class LogsError(models.Model):

    date = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    created_timestamp = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления"
                                             )
    type_error = models.CharField(
        max_length=20, choices=TYPE_LOGS_ERROR, default="error"
    )
    location = models.CharField(
        "Место ошибки",
        max_length=200,
        blank=True,
        null=True,
    )
    info = models.CharField(
        "Инфо о ошибке",
        max_length=100000,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Лог ошибок"
        verbose_name_plural = "Логи ошибок"

    def __str__(self):
        return f"Тип ошибки: {self.type_error},{self.date} "


class LogsAddProduct(models.Model):

    date = models.DateField(auto_now=True, verbose_name="Дата добавления")
    created_timestamp = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления"
                                             )
    product = models.ForeignKey(
        Product,
        verbose_name="Товар",
        on_delete=models.CASCADE,
    )

    info = models.CharField(
        "Инфо",
        max_length=4000,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Лог добавления товара"
        verbose_name_plural = "Логи добавления товара"

    def __str__(self):
        return f"Товар: {self.product} "

class LogsInfoError(models.Model):

    date = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    created_timestamp = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления"
                                             )
    type_error = models.CharField(
        max_length=20, choices=TYPE_LOGS_ERROR, default="error"
    )
    location = models.CharField(
        "Место ошибки",
        max_length=200,
        blank=True,
        null=True,
    )
    info = models.CharField(
        "Инфо о ошибке",
        max_length=20000,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Информационные сообщения"
        verbose_name_plural = "Информационные сообщения"

    def __str__(self):
        return f"Тип ошибки: {self.type_error},{self.date} "
    
class LogsOrderError(models.Model):

    date = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    created_timestamp = models.DateTimeField(default=timezone.now, verbose_name="Дата добавления"
                                             )
    type_error = models.CharField(
        max_length=20, choices=TYPE_LOGS_ERROR, default="error"
    )
    location = models.CharField(
        "Место ошибки",
        max_length=200,
        blank=True,
        null=True,
    )
    info = models.CharField(
        "Инфо о ошибке",
        max_length=20000,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Логи фоновые по сделкам"
        verbose_name_plural = "Логи фоновые по сделкам"

    def __str__(self):
        return f"Тип ошибки: {self.type_error},{self.date} "

