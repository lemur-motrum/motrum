from django.db import models
from django.test import Client

# Create your models here.
class NotificationTemplate(models.Model):
    key = models.CharField("Ключ", max_length=30)
    name = models.CharField("Название", max_length=60)
    header = models.CharField("Заголовок", max_length=150)
    text = models.CharField("Текст", max_length=300)

    class Meta:
        verbose_name = "Шаблон уведомления"
        verbose_name_plural = "Шаблоны уведомлений"

    def __str__(self):
        return self.name
    
class Notification(models.Model):
    client = models.ForeignKey(Client, verbose_name="Клиент", on_delete=models.CASCADE)
    template = models.ForeignKey(
        NotificationTemplate, verbose_name="Шаблон", on_delete=models.CASCADE
    )
    header = models.CharField("Вставка в заголовок", max_length=150)
    text = models.CharField("Текст", max_length=300)
    date = models.DateTimeField("Дата и время", auto_now_add=True)
    is_viewed = models.BooleanField("Прочитано", default=False)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ("is_viewed", "-date")    
    
