from pyexpat import model
from django.db import models

# Create your models here.
from simple_history.models import HistoricalRecords, HistoricForeignKey

from apps.specification.models import Specification
from apps.user.models import CustomUser


class Client(CustomUser):
    user = models.OneToOneField(CustomUser, parent_link=True, on_delete=models.CASCADE)
    contact_name = models.CharField("Контактное лицо", max_length=40, blank=True, null=True)
    phone = models.CharField("Номер телефона", max_length=40,unique=True)
    # manager = models.OneToOneField(CustomUser, parent_link=True, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        
    def save(self, *args, **kwargs):
        # self.password = "1234"
        # self.set_password(self.password)
        self.username = self.phone


        super().save(*args, **kwargs)     

    def __str__(self):
        return self.phone


class Requisites(models.Model):
    client = models.ForeignKey(Client,verbose_name="Клиент", on_delete=models.CASCADE)
    contract = models.CharField(
        "Договор",
        max_length=50,
        null=True,
    )

    legal_entity = models.CharField(
        "Юридическое лицо",
        max_length=150,
    )
    inn = models.CharField(
        "ИНН",max_length=12,
    )
    kpp = models.CharField(
        "КПП",max_length=10,
    )
    ogrn = models.CharField(
        "ОГРН",max_length=15,
    )
    legal_post_code = models.PositiveIntegerField(
        "Юридический адрес :индекс",
    )
    legal_city = models.CharField(
        "Юридический адрес : город",
        max_length=50,
    )
    legal_address = models.CharField(
        "Юридический адрес : адрес",
        max_length=200,
    )
    postal_post_code = models.CharField(
        "Почтовый адрес :индекс",max_length=10,
    )
    postal_city = models.CharField(
        "Почтовый адрес : город",
        max_length=50,
    )
    postal_address = models.CharField(
        "Почтовый адрес : адрес",
        max_length=200,
    )
    class Meta:
        verbose_name = "Реквизиты"
        verbose_name_plural = "Реквизиты"

    # def __str__(self):
    #     return self.name


class AccountRequisites(models.Model):
    requisites = models.ForeignKey(Requisites,verbose_name="Реквизиты", on_delete=models.CASCADE)
    account_requisites = models.CharField(
        "Расчётный счёт", max_length=30,
    )
    bank = models.CharField(
        "Банк",
        max_length=200,
    )
    kpp = models.CharField(
        "КПП",max_length=10,
    )
    bic = models.CharField(
        "БИК",max_length=10,
    )
    class Meta:
        verbose_name = "Расчётный счёт"
        verbose_name_plural = "Расчётные счёта"

    def __str__(self):
        return self.account_requisites


class ClientDiscount(models.Model):
    requisites = models.OneToOneField(Requisites,verbose_name="Юр.лицо", on_delete=models.CASCADE)
    percent = models.FloatField(
            "Процент скидки",
        )
    
    class Meta:
        verbose_name = "Скидка юрлица"
        verbose_name_plural = "Скидки юрлиц"

    def __str__(self):
        return self.name
    
STATUS_ORDER = (
    ("BASE", "В обработке"),
    ("PRODUCT", "Счёт на оплату"),
    ("CATALOG", "Заказ у поставщика"),
    ("ALL", "На доставке "),
    ("ALL", "Готов к отгрузке самовывозом"),
    ("ALL", "Отменен"),
    ("ALL", "Заказ завершен")
)  
class Order(models.Model):
    client =  models.OneToOneField(Client,verbose_name="Клиент", on_delete=models.PROTECT)
    name = models.PositiveIntegerField(
        "номер заказа",
    )
    status =  models.CharField(max_length=100, choices=STATUS_ORDER, default="ALL")
    specification = models.OneToOneField(Specification,verbose_name="Спецификация", on_delete=models.PROTECT)
    
    