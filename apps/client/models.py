from django.db import models

# Create your models here.


class Client(models.Model):
    client_name = models.CharField("имя клиента", max_length=200)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.client_name
