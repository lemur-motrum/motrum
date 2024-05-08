from multiprocessing.connection import Client
from django.db import models
from django.utils import timezone

from apps.product.models import Product
from apps.supplier.models import Discount
from apps.user.models import AdminUser

# Create your models here.

class Specification(models.Model):
    id_bitrix = models.PositiveIntegerField(
        "номер сделки битрикс"
    )
    date = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    date_stop = models.DateField(default=timezone.now, verbose_name="Дата окончания")
    currency_product = models.BinaryField("валютные товары в спецификации")
    tag_stop = models.BinaryField("недействительно")
    wholesale = models.ForeignKey(
        Discount,
        verbose_name="Скидка оптовая",
        on_delete=models.PROTECT,
    )
    total_amount = models.IntegerField("процент скидки")
    admin_creator = models.ForeignKey(
        AdminUser,
        on_delete=models.PROTECT,
    )
    file = models.CharField("фаил в системе", max_length=40)
    
    # client = models.ForeignKey(
    #     Client,
    #     on_delete=models.PROTECT,
    # )
    

    class Meta:
        verbose_name = "Спецификация"
        verbose_name_plural = "Спецификации"

    def __str__(self):
        return self.id

class ProductSpecification(models.Model):
    specification = models.ForeignKey(
        Specification,
        on_delete=models.PROTECT,
    )   
    product =  models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )  
    quantity = models.IntegerField("количество товара")
    price_one = models.IntegerField("цена одного на момент формирования")
    price_all = models.IntegerField("цена всего товара на момент формирования")
        