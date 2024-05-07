from django.db import models


# Create your models here.


class Supplier(models.Model):
    name = models.CharField("Название поставщика", max_length=30)
    # integration_type (тип интеграции)

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.name


class Vendor(models.Model):
    name = models.CharField("Название производителя", max_length=30)
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="Производитель",
        on_delete=models.PROTECT,
    )
    currency_catalog = models.ForeignKey(
        "product.Currency",
        verbose_name="Производитель",
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = "Производитель"
        verbose_name_plural = "Производители"

    def __str__(self):
        return self.name


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
