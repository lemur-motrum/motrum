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

class Text1(models.Model):
  
    name = models.CharField("имя клиента", max_length=25, blank=True, null=True)
    history = HistoricalRecords()
   
    def __str__(self):
        return self.name
    
class Text2(models.Model):
    name = models.CharField("имя клиента", max_length=25, blank=True, null=True)
    testtest = HistoricForeignKey(
        Text1,
        related_name="Text2",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
 
    def __str__(self):
        return self.name    



