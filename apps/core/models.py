from django.db import models

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


class Vat(models.Model):
    name = models.SmallIntegerField("процент ндс")
    
    class Meta:
        verbose_name = "НДС"
        verbose_name_plural = "НДС"

    def __str__(self):
        return str(self.name )+ "%"