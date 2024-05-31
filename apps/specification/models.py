import datetime
from multiprocessing.connection import Client
from django.db import models
from django.utils import timezone

from apps.core.models import Currency
from apps.core.utils import create_time
from apps.product.models import Price, Product
from apps.supplier.models import Discount
from apps.user.models import AdminUser

# Create your models here.


class Specification(models.Model):
    id_bitrix = models.PositiveIntegerField("номер сделки битрикс")
    date = models.DateField(
        default=datetime.datetime.now, verbose_name="Дата добавления"
    )
    date_stop = models.DateField(default=create_time(), verbose_name="Дата окончания")
    currency_product = models.BooleanField(
        "валютные товары в спецификации", default=False
    )
    tag_stop = models.BooleanField("недействительно", default=False)
    wholesale = models.ForeignKey(
        Discount,
        verbose_name="Скидка оптовая",
        on_delete=models.PROTECT,
        null=True,
        default=None,
    )

    total_amount = models.IntegerField("процент скидки", null=True, default=None)
    admin_creator = models.ForeignKey(
        AdminUser, on_delete=models.PROTECT, null=True, default=None
    )
    file = models.CharField("фаил в системе", max_length=40, null=True, default=None)
    tag_currency = models.ForeignKey(
        Currency, on_delete=models.PROTECT, null=True, default=None
    )
    #  tag_currency = models.BinaryField("Валютная отметка",default=False)
    # client = models.ForeignKey(
    #     Client,
    #     on_delete=models.PROTECT,
    # )

    class Meta:
        verbose_name = "Спецификация"
        verbose_name_plural = "Спецификации"

    def __str__(self):
        return f"{self.id_bitrix}"


class ProductSpecification(models.Model):
    specification = models.ForeignKey(
        Specification,
        on_delete=models.PROTECT,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )


    quantity = models.IntegerField("количество товара")
    price_one = models.IntegerField("цена одного на момент формирования")
    price_all = models.IntegerField("цена всего товара на момент формирования")

    class Meta:
        verbose_name = "Спецификация продукт"
        verbose_name_plural = "Спецификации Продукты"

    # def __str__(self):
    #     return self.id

    def save(self, *args, **kwargs):
        spec = Specification.objects.get(id=self.specification.id)
        price = Price.objects.get(prod=self.product)
        print()
        price_current = price.currency.words_code
        self.price_one = price.price_motrum
        self.price_all =  self.price_one * self.quantity
        if price_current != "RUB":
            spec.tag_currency = True
            spec.save()

        super().save(*args, **kwargs)
