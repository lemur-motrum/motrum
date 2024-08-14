from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Currency(models.Model):
    name = models.CharField("Название валюты", max_length=30)
    words_code = models.CharField("Букв. код", max_length=30)
    code = models.SmallIntegerField("Цифр. код")

    class Meta:
        verbose_name = "Валюта"
        verbose_name_plural = "Валюты"

    def __str__(self):
        return self.name


class CurrencyPercent(models.Model):
    percent = models.FloatField("Процент умножения валютных цен")

    class Meta:
        verbose_name = "Процент умножения валютных цен"
        verbose_name_plural = "Процент умножения валютных цен"

    def __str__(self):
        return f"Процент умножения валютных цен: {self.percent}%"


class Vat(models.Model):
    name = models.SmallIntegerField("Процент ндс")

    class Meta:
        verbose_name = "НДС"
        verbose_name_plural = "НДС"

    def __str__(self):
        return str(self.name) + "%"


class CalendarHoliday(models.Model):
    year = models.CharField("Год", max_length=30)
    json_date = models.JSONField("Список выходных из консультанта")

    class Meta:
        verbose_name = "Даты выходных и праздников"

# class User(AbstractUser):
#     pass