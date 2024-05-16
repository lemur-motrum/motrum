import os
from django.db import models
import requests
import json
from django.utils.text import slugify
from pytils import translit


from apps.core.models import Currency, Vat

# from apps.product.models import CategoryProduct, Product


# Create your models here.


class Supplier(models.Model):
    name = models.CharField("Название поставщика", max_length=40)
    # integration_type (тип интеграции)
    slug = models.SlugField(null=True)

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug_text = self
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)
    
        super(Supplier, self).save(*args, **kwargs)


class Vendor(models.Model):
    name = models.CharField("Название производителя", max_length=40)
    slug = models.SlugField(null=True)
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="Поставщик",
        on_delete=models.PROTECT,
    )
    currency_catalog = models.ForeignKey(
        Currency,
        verbose_name="Валюта каталога",
        on_delete=models.PROTECT,
    )
    vat_catalog = models.ForeignKey(
        Vat,
        verbose_name="Ндс в каталоге",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    # vat_catalog_check = models.BinaryField("входит ли в цену получаемую от поставщика" blank=True,
    #     null=True,)

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug_text = self.name
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)

        super(Vendor, self).save(*args, **kwargs)


# class ListApiUploadIek(models.Model):
#     name = models.CharField("товары необходимые для загрузки апи иек", max_length=30)


class SupplierCategoryProduct(models.Model):
    name = models.CharField("Название категории", max_length=30)
    article_name = models.CharField("Артикул категории", max_length=25)

    category_catalog = models.ForeignKey(
        "product.CategoryProduct",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "Категория товара у поставщика"
        verbose_name_plural = "Категории товаров у поставщика"

    def __str__(self):
        return self.name


class SupplierGroupProduct(models.Model):
    name = models.CharField("Название группы", max_length=30)
    article_name = models.CharField("Артикул группы", max_length=25)
    category_supplier = models.ForeignKey(
        SupplierCategoryProduct,
        on_delete=models.PROTECT,
    )
    group_catalog = models.ForeignKey(
        "product.CategoryProduct",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "Группа товара у поставщика"
        verbose_name_plural = "Группы товаров у поставщика"

    def __str__(self):
        return self.name


class Discount(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="Поставщик",
        on_delete=models.PROTECT,
    )
    vendor = models.ForeignKey(
        Vendor,
        verbose_name="Производитель",
        on_delete=models.PROTECT,
    )
    category_catalog = models.ForeignKey(
        "product.CategoryProduct",
        verbose_name="Категория каталога",
        on_delete=models.PROTECT,
        blank=True, null=True
        
    )
    
    group_catalog = models.ForeignKey(
        "product.GroupProduct",
        verbose_name="Группа каталога",
        on_delete=models.PROTECT,
        blank=True, null=True
    )
    percent = models.SmallIntegerField("процент скидки")

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"

    def __str__(self):
        return "Скидка" + str(self.vendor) + str(self.vendor) + str(self.percent) + "%"


class SupplierCategoryProductAll(models.Model):
    name = models.CharField("Название категории", max_length=50)
    article_name = models.CharField("Артикул категории", max_length=25)
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="Поставщик",
        on_delete=models.PROTECT,
    )
    category_catalog = models.ForeignKey(
        "product.CategoryProduct",
        verbose_name="Категория каталога",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    group_catalog = models.ForeignKey(
        "product.GroupProduct",
        verbose_name="Группа каталога",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Категории товара у поставщиков"
        verbose_name_plural = "Категории товаров у поставщиков"

    def __str__(self):
        return self.name
