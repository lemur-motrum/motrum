import datetime
from mimetypes import init
from multiprocessing.connection import Client
from django.db import models
from django.utils import timezone

from apps.core.models import Currency, Vat
from apps.core.utils import create_time
from apps.product.models import Price, Product
from apps.specification.utils import get_document_path
from apps.supplier.models import Discount

# from apps.user.models import CustomAdminUser
from django.db.models import Count, Sum

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
    tag_stop = models.BooleanField("Действительно", default=True)
    wholesale = models.ForeignKey(
        Discount,
        verbose_name="Скидка оптовая",
        on_delete=models.PROTECT,
        null=True,
        default=None,
    )

    total_amount = models.FloatField("Сумма спецификации", null=True, default=None)
    admin_creator = models.ForeignKey(
        AdminUser,
        on_delete=models.PROTECT,
        verbose_name="Администратор",
        null=True,
        default=None,
    )
    file = models.FileField(
        "фаил", upload_to=get_document_path, null=True, default=None
    )
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
        verbose_name="Товар",
        blank=True,
        null=True,
    )
    
    product = models.ForeignKey(
        Product,
        verbose_name="Продукты",
        on_delete=models.PROTECT,
    )



    quantity = models.IntegerField("количество товара",blank=True,
        null=True,)
    price_one = models.FloatField("цена одного на момент формирования")
    price_all = models.FloatField("цена всего товара на момент формирования",blank=True,
        null=True,)
    price_exclusive = models.BooleanField("Цена по запросу", default=False)
   

    
    class Meta:
        verbose_name = "Спецификация продукт"
        verbose_name_plural = "Спецификации Продукты"

    def __str__(self):
        return f"{self.product}"



    def save(self, *args, **kwargs):
    
  
        spec = Specification.objects.get(id=self.specification.id)
        price = Price.objects.get(prod=self.product)
        # self.price_one = self.price_one
        if self.price_one != price.price_supplier:
            self.price_exclusive = True
        price_current = price.currency.words_code
        
        self.price_all = self.price_one * self.quantity
        # отметка о валютности + добавление общец суммы
        if price_current != "RUB":
            spec.tag_currency = True
        if spec.total_amount is None:
            total_init = 0
        else:
            
            total_init = spec.total_amount
        total = total_init + self.price_all
        spec.total_amount = total
        spec.save()

        
        super().save(*args, **kwargs)
