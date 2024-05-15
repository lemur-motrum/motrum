import os
from django.utils import timezone
from django.db import models

from apps import core
from apps.core.models import Currency, Vat

# from apps.core.utils import get_image_path
from apps.supplier.models import Supplier, Vendor
from pytils import translit
from django.utils.text import slugify
from project.settings import BASE_DIR, MEDIA_ROOT
from django.utils.safestring import mark_safe

# Create your models here.


class Product(models.Model):
    article = models.PositiveIntegerField("Артикул мотрум", blank=False)
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="Поставщик",
        related_name="products",
        on_delete=models.PROTECT,
    )
    vendor = models.ForeignKey(
        Vendor,
        verbose_name="Производитель",
        on_delete=models.PROTECT,
    )

    article_supplier = models.CharField("Артикул поставщика", max_length=50)
    additional_article_supplier = models.CharField(
        "Дополнительный артикул поставщика", max_length=50, null=True
    )
    category = models.ForeignKey(
        "CategoryProduct", verbose_name="Категория", on_delete=models.PROTECT, null=True
    )
    group = models.ForeignKey(
        "GroupProduct", verbose_name="Группа", on_delete=models.PROTECT, null=True
    )
    description = models.CharField("Описание товара", max_length=1000, null=True)
    name = models.CharField("Название товара", max_length=50)
    price = models.ForeignKey("Price", on_delete=models.CASCADE, null=True)
    stock = models.ForeignKey("Stock", on_delete=models.CASCADE, null=True)
    check_image_upgrade = models.BooleanField("было изменено вручную", default=False)
    check_document_upgrade = models.BooleanField("было изменено вручную", default=False)
    check_property_upgrade = models.BooleanField("было изменено вручную", default=False)
    data_create = models.DateField(default=timezone.now, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return str(self.article)


class CategoryProduct(models.Model):
    name = models.CharField("Название категории", max_length=50)

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return self.name


class GroupProduct(models.Model):
    name = models.CharField("Название группы", max_length=50)
    article_name = models.CharField("Артикул группы", max_length=25)
    category = models.ForeignKey(
        CategoryProduct,
        verbose_name="категория",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "Группа товара"
        verbose_name_plural = "Группы товаров"

    def __str__(self):
        return self.name


class Price(models.Model):
    prod = models.OneToOneField(
        Product,
        related_name="prod_price",
        on_delete=models.PROTECT,null=True
    )
    currency = models.ForeignKey(
        Currency,
        verbose_name="Валюта",
        on_delete=models.PROTECT,
    )
    vat = models.ForeignKey(
        Vat,
        verbose_name="НДС",
        on_delete=models.PROTECT,
    )
    price_supplier = models.FloatField("Цена в каталоге поставщика в валюте каталога")
    rub_price_supplier = models.FloatField("Цена в каталоге поставщика в рублях")
    price_motrum = models.FloatField("Цена поставщика для Motrum в рублях")

    class Meta:
        verbose_name = "Цена"
        verbose_name_plural = "Цены"

    def __str__(self):
        return f"{self.rub_price_supplier} {self.price_motrum}"


class CurrencyRate(models.Model):
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
    )

    date = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    rate = models.PositiveIntegerField("курс ЦБ")


class Stock(models.Model):
    prod = models.OneToOneField(
        Product,
        related_name="prod_stock",
        on_delete=models.PROTECT,null=True
    )
    lot = models.ForeignKey("Lot",verbose_name = "Единица измерения поставщика", on_delete=models.PROTECT)
    stock_supplier = models.PositiveIntegerField(
        "Остаток на складе поставщика в единицах поставщика"
    )
    lot_complect = models.PositiveIntegerField("Содержание набора (комплекта) в штуках")
    stock_supplier_unit = models.PositiveIntegerField(
        "Остаток на складе поставщика в штуках"
    )
    stock_motrum = models.PositiveIntegerField("Остаток на складе Motrum в штуках")

    class Meta:
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"

    def __str__(self):
        return f"{self.stock_supplier} {self.stock_supplier}"


class Lot(models.Model):
    name = models.CharField("Полное название", max_length=30)
    name_shorts = models.CharField("Короткое название", max_length=6, null=True)
    slug = models.SlugField(null=True)

    class Meta:
        verbose_name = "Единица измерения поставщика"
        verbose_name_plural = "Единицы измерений поставщиков"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug_text = self.name
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)

        super(Lot, self).save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        # on_delete=models.PROTECT,
    )
    photo = models.ImageField(
        "Изображение", upload_to="core.utils.get_file_path", null=True
    )
    file = models.CharField("фаил в системе", max_length=100, null=True)
    link = models.CharField("ссылка у поставщика", max_length=100)
    hide = models.BooleanField("скрыть", default=False)
    
    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self):
            return mark_safe(
                '<img src="{}" height="100" />'.format(self.photo)
            )

class ProductDocument(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        # on_delete=models.PROTECT,
    )
    document = models.FileField(
        "Документ", upload_to="core.utils.get_file_path", null=True
    )
    file = models.CharField("фаил в системе", max_length=100, null=True)
    link = models.CharField("ссылка у поставщика", max_length=100, null=True)
    hide = models.BooleanField("скрыть", default=False)
    
    class Meta:
        verbose_name = "Документация"
        verbose_name_plural = "Документации"

    def __str__(self):
        return f"{self.document}"


class ProductProperty(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        # on_delete=models.PROTECT,
    )
    name = models.CharField("название", max_length=40)
    value = models.CharField("значение", max_length=40)
    unit_measure = models.CharField("значение", max_length=40, null=True)
    hide = models.BooleanField("скрыть", default=False)

    class Meta:
        verbose_name = "Характеристика \свойства"
        verbose_name_plural = "Характеристики\свойства"

    def __str__(self):
        return f"{self.name}:{self.value}"
