from email.policy import default
import os
from pyexpat import model
from django.utils import timezone
from django.db import models

from apps import core
from apps.core.models import Currency, Vat
from smart_selects.db_fields import ChainedForeignKey


from apps.core.utils import (
    create_article_motrum,
    get_file_path,
    get_file_path_add,
    get_lot,
    get_price_motrum,
    get_price_supplier_rub,
)
from apps.supplier.models import Discount, Supplier, SupplierCategoryProductAll, Vendor
from pytils import translit
from django.utils.text import slugify
from project.settings import BASE_DIR, MEDIA_ROOT, MEDIA_URL
from django.utils.safestring import mark_safe
TYPE_DOCUMENT = (
    ("InstallationProduct", "Руководство по монтажу и эксплуатации"),
    ("DimensionDrawing", "Габаритные чертежи"),
    ("Passport", "Паспорт"),
    ("WiringDiagram", "Схема подключения"),
    ("Models3d", "3D модели"),
    ("Brochure", "Брошюра"),
    ("Certificates", "Сертификат"),
    ("Other", "Другое"),
)
# Create your models here.


class Product(models.Model):
    article = models.PositiveIntegerField("Артикул мотрум", blank=False)
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="Поставщик",
        # related_name="products",
        on_delete=models.PROTECT,
    )
    vendor = ChainedForeignKey(
        Vendor,
        chained_field="supplier",
        chained_model_field="supplier",
        verbose_name="Производитель",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    article_supplier = models.CharField("Артикул поставщика", max_length=50)
    additional_article_supplier = models.CharField(
        "Дополнительный артикул поставщика", max_length=50, blank=True, null=True
    )
    category_supplier_all = models.ForeignKey(
        SupplierCategoryProductAll,
        verbose_name="Приходящая категории товара от поставщиков",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        "CategoryProduct",
        verbose_name="Категория",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    group = models.ForeignKey(
        "GroupProduct",
        verbose_name="Группа",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    description = models.CharField(
        "Описание товара", max_length=1000, blank=True, null=True
    )
    name = models.CharField("Название товара", max_length=350)
    check_image_upgrade = models.BooleanField("было изменено вручную", default=False)
    check_document_upgrade = models.BooleanField("было изменено вручную", default=False)
    check_property_upgrade = models.BooleanField("было изменено вручную", default=False)
    data_create = models.DateField(default=timezone.now, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"Артикул мотрум:{self.article} Название товара:{self.name}"

    def save(self, *args, **kwargs):
        if self.article == None:
            article = create_article_motrum(self.supplier.id, self.vendor.id)
            self.article = article
        super().save(*args, **kwargs)
        # обновление цен товаров
        price = Price.objects.filter(prod=self.id)
        for price_one in price:
            price_one.price_supplier = price_one.price_supplier
            price_one.save()


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
        on_delete=models.CASCADE,
        blank=True,
        null=True,
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
        blank=True,
        null=True,
    )
    vat_include = models.BooleanField("Включен ли налог в цену", default=True)

    price_supplier = models.FloatField(
        "Цена в каталоге поставщика в валюте каталога",
        blank=True,
        null=True,
    )

    rub_price_supplier = models.FloatField(
        "Цена в каталоге поставщика в рублях + НДС",
        blank=True,
        null=True,
    )
    price_motrum = models.FloatField(
        "Цена поставщика для Motrum в рублях",
        blank=True,
        null=True,
    )

    sale = models.ForeignKey(
        Discount,
        verbose_name="Примененная скидка",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Цена"
        verbose_name_plural = "Цены"

    def __str__(self):
        return f"{self.rub_price_supplier} {self.price_motrum}"

    def save(self, *args, **kwargs):
        print(self.price_supplier)
        if self.price_supplier is not None:
            rub_price_supplier = get_price_supplier_rub(
                self.currency.words_code,
                self.vat.name,
                self.vat_include,
                self.price_supplier,
            )

            self.rub_price_supplier = rub_price_supplier
            price_motrum_all = get_price_motrum(
                self.prod.category_supplier_all.category_supplier,
                self.prod.category_supplier_all.group_supplier,
                self.prod.vendor,
                rub_price_supplier,
                self.prod.category_supplier_all,
            )
            price_motrum = price_motrum_all[0]
            sale = price_motrum_all[1]
            self.price_motrum = price_motrum
            self.sale = sale

        super().save(*args, **kwargs)


class CurrencyRate(models.Model):
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
    )

    date = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    value = models.FloatField("курс ЦБ", blank=True, null=True)
    vunit_rate = models.FloatField("курс ЦБ за еденицу", blank=True, null=True)
    count = models.PositiveIntegerField("Единиц", blank=True, null=True)


class Stock(models.Model):
    prod = models.OneToOneField(
        Product,
        related_name="prod_stock",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    lot = models.ForeignKey(
        "Lot",
        verbose_name="Единица измерения поставщика",
        on_delete=models.PROTECT,
    )
    stock_supplier = models.PositiveIntegerField(
        "Остаток на складе поставщика в единицах поставщика"
    )
    lot_complect = models.PositiveIntegerField(
        "Содержание набора (комплекта) в штуках", default=1
    )
    stock_supplier_unit = models.PositiveIntegerField(
        "Остаток на складе поставщика в штуках"
    )
    stock_motrum = models.PositiveIntegerField("Остаток на складе Motrum в штуках")

    class Meta:
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"

    def __str__(self):
        return f"{self.stock_supplier} {self.stock_supplier}"

    def save(self, *args, **kwargs):

        lots = get_lot(self.lot.name, self.stock_supplier, self.lot_complect)

        self.stock_supplier_unit = lots[1]
        self.lot_complect = lots[2]

        super().save(*args, **kwargs)


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
    photo = models.ImageField("Изображение", upload_to=get_file_path_add, null=True)
    # file = models.CharField("фаил в системе", max_length=100, null=True)
    link = models.CharField("ссылка у поставщика", max_length=100)
    hide = models.BooleanField("скрыть", default=False)

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    def __str__(self):
        return mark_safe(
            '<img src="{}{}" height="100" width="100" />'.format(MEDIA_URL, self.photo)
        )

    # def delete(self, *args, **kwargs):
    #     self.hide = True
    #     super().save(*args, **kwargs)  # Call the "real" save() method.


class ProductDocument(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    document = models.FileField("Документ", upload_to=get_file_path_add, null=True)
    # file = models.CharField("фаил в системе", max_length=100, null=True)
    # type_doc = models.CharField("Тип документации", max_length=150, null=True)
    type_doc = models.CharField("Тип документации",
        max_length=40, choices=TYPE_DOCUMENT, default="Other"
    )
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
       
    )
    name = models.CharField("название", max_length=100)
    value = models.CharField("значение", max_length=100)
    unit_measure = models.CharField("значение", max_length=100, null=True)
    hide = models.BooleanField("скрыть", default=False)

    class Meta:
        verbose_name = "Характеристика \свойства"
        verbose_name_plural = "Характеристики\свойства"

    def __str__(self):
        return f"{self.name}:{self.value}"
