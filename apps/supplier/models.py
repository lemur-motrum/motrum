import os
from django.db import models
import requests
import json
from django.utils.text import slugify
from pytils import translit


from apps.core.models import Currency


# Create your models here.


class Supplier(models.Model):
    name = models.CharField("Название поставщика", max_length=30)
    # integration_type (тип интеграции)
    slug = models.SlugField(null=True)

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

    # def __str__(self):
    #     return self.name

    def save(self, *args, **kwargs):
        slug_text = self.name
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)

        super(Supplier, self).save(*args, **kwargs)

    @staticmethod
    def prompower_api():

        url = "https://prompower.ru/api/prod/getProducts"
        payload = json.dumps(
            {
                "email": os.environ.get("PROMPOWER_API_EMAIL"),
                "key": os.environ.get("PROMPOWER_API_KEY"),
            }
        )
        headers = {
            "Content-type": "application/json",
            "Cookie": "nuxt-session-id=s%3Anp9ngMJIwPPIJnpKt1Xow9DA50eUD5OQ.IwH2nwSHFODHMKNUx%2FJRYeOVF9phtKXSV6dg6QQebAU",
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        data = response.json()
        prompower = Supplier.objects.get(slug="prompower")
        print(prompower.id)
        category_all = []
        for data_item in data:
            category = {
                "name": data_item["category"],
                # "article_name": data_item["tnved"], тн вед это по таможенной жекларации номер где то есть где то нет где на одном товрае одинаковый
                "supplier": prompower.id,
            }
            category_all.append(category)
      
        unique_category = [dict(t) for t in {frozenset(d.items()) for d in category_all}]
        
        # for category in unique_category:
        #     SupplierCategoryProductTest.create(name=category['name'], article_name=0, supplier=category['supplier'])
        

        return unique_category


class Vendor(models.Model):
    name = models.CharField("Название производителя", max_length=30)
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

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

    # def __str__(self):
    #     return self.name

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
        SupplierCategoryProduct,
        on_delete=models.PROTECT,
    )
    group_catalog = models.ForeignKey(
        SupplierGroupProduct,
        on_delete=models.PROTECT,
    )
    percent = models.SmallIntegerField("процент скидки")


class SupplierCategoryProductTest(models.Model):
    name = models.CharField("Название категории", max_length=30)
    article_name = models.CharField("Артикул категории", max_length=25)
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="Поставщик",
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return self.name
