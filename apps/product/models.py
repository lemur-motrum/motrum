from django.utils import timezone
from django.db import models

from apps.supplier.models import Supplier, Vendor

# Create your models here.


class Product(models.Model):
    article = models.PositiveIntegerField("Артикул мотрум", blank=False)
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="Производитель",
        related_name="products",
        on_delete=models.PROTECT,
    )
    vendor = models.ForeignKey(
        Vendor,
        verbose_name="Поставщик",
        on_delete=models.PROTECT,
    )
    article_supplier = models.CharField("Артикул поставщика", max_length=50)
    additional_article_supplier = models.CharField(
        "Дополнительный артикул поставщика", max_length=50
    )
    category = models.ForeignKey(
        "CategoryProduct",
        verbose_name="Поставщик",
        on_delete=models.PROTECT,
    )
    group = models.ForeignKey(
        "GroupProduct",
        on_delete=models.PROTECT,
    )

    name = models.CharField("Название товара", max_length=50)
    price = models.ForeignKey("Price", on_delete=models.PROTECT)
    stock = models.ForeignKey("Stock", on_delete=models.PROTECT)
    check_image_upgrade = models.BinaryField("было изменено вручную")
    check_document_upgrade = models.BinaryField("было изменено вручную")
    check_property_upgrade = models.BinaryField("было изменено вручную")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.article


class CategoryProduct(models.Model):
    name = models.CharField("Название категории", max_length=30)

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return self.name


class GroupProduct(models.Model):
    name = models.CharField("Название группы", max_length=30)
    article_name = models.CharField("Артикул группы", max_length=25)
    category = models.ForeignKey(
        CategoryProduct,
        verbose_name="категория",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "Группа товара"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.name


class Price(models.Model):
    currency = models.ForeignKey(
        "Currency",
        on_delete=models.PROTECT,
    )
    vat = models.ForeignKey(
        "Vat",
        on_delete=models.PROTECT,
    )
    price_supplier = models.PositiveIntegerField(
        "Цена в каталоге поставщика в валюте каталога"
    )
    rub_price_supplier = models.PositiveIntegerField(
        "Цена в каталоге поставщика в рублях"
    )
    price_motrum = models.PositiveIntegerField("Цена поставщика для Motrum в рублях")


class Currency(models.Model):
    name = models.CharField("Название валюты", max_length=30)
    words_code = models.CharField("Букв. код", max_length=30)
    code = models.SmallIntegerField("Цифр. код")


class Vat(models.Model):
    code = models.SmallIntegerField("процент ндс")


class CurrencyRate(models.Model):
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
    )

    date = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    rate = models.PositiveIntegerField("курс ЦБ")


class Stock(models.Model):
    lot = models.ForeignKey("Lot", on_delete=models.PROTECT)
    stock_supplier = models.PositiveIntegerField(
        "Остаток на складе поставщика в единицах поставщика"
    )
    lot_complect = models.PositiveIntegerField("Содержание набора (комплекта) в штуках")
    stock_supplier_unit = models.PositiveIntegerField(
        "Остаток на складе поставщика в штуках"
    )
    stock_motrum = models.PositiveIntegerField("Остаток на складе Motrum в штуках")


class Lot(models.Model):
    name = models.CharField("Единица измерения поставщика", max_length=30)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )
    file = models.CharField("фаил в системе", max_length=40)
    link = models.CharField("ссылка у поставщика", max_length=40)
    hide = models.BinaryField("скрыть")


class ProductDocument(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )
    file = models.CharField("фаил в системе", max_length=40)
    link = models.CharField("ссылка у поставщика", max_length=40)
    hide = models.BinaryField("скрыть")


class ProductProperty(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )
    name = models.CharField("название", max_length=40)
    value = models.CharField("значение", max_length=40)
    unit_measure = models.CharField("значение", max_length=40)
    hide = models.BinaryField("скрыть")
