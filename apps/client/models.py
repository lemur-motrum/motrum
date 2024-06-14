from django.db import models

# Create your models here.
from simple_history.models import HistoricalRecords, HistoricForeignKey

class Client(models.Model):
  
    name = models.CharField("имя клиента", max_length=25, blank=True, null=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        return self.name
