from email.policy import default

import os
from pyexpat import model
from django.utils import timezone
from django.db import models
from simple_history import register
from simple_history.utils import update_change_reason
from apps import core
from apps.core.models import Currency, Vat
from django.db.models.deletion import CASCADE
from django.db.models.signals import post_save
from django.dispatch import receiver
from simple_history.models import HistoricalRecords, HistoricForeignKey
from simple_history.models import (
    SIMPLE_HISTORY_REVERSE_ATTR_NAME,
    DeletedObject,
    HistoricalRecords,
    ModelChange,
    ModelDelta,
    is_historic,
    to_historic,
)


from django.dispatch import receiver
from django.db.models import signals, Sum, Q

from apps.core.utils import (
    create_article_motrum,
    get_file_path,
    get_file_path_add,
    get_lot,
    get_motrum_category,
    get_price_motrum,
    get_price_supplier_rub,
)
from simple_history.signals import (
    pre_create_historical_record,
    post_create_historical_record,
    pre_create_historical_m2m_records,
    post_create_historical_m2m_records,
)
from apps.supplier.models import (
    Discount,
    Supplier,
    SupplierCategoryProduct,
    SupplierCategoryProductAll,
    SupplierGroupProduct,
    Vendor,
)
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
    ("Soft", "Программы"),
    ("Doc", "Руководства и Спецификации"),
    ("Text", "Тексты"),
)
# Create your models here.




class Product(models.Model):
    article = models.CharField("Артикул мотрум", max_length=50, blank=False)
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="Поставщик",
        # related_name="products",
        on_delete=models.PROTECT,
    )
    vendor = models.ForeignKey(
        Vendor,
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
        verbose_name="Подгруппа категории товара от поставщиков",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    group_supplier = models.ForeignKey(
        SupplierGroupProduct,
        verbose_name="Группа товара от поставщиков",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    category_supplier = models.ForeignKey(
        SupplierCategoryProduct,
        verbose_name="Категории товара от поставщиков",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        "CategoryProduct",
        verbose_name="Категория Мотрум",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    group = models.ForeignKey(
        "GroupProduct",
        verbose_name="Группа Мотрум",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    description = models.CharField(
        "Описание товара", max_length=4000, blank=True, null=True
    )

    name = models.CharField("Название товара", max_length=600)
    check_image_upgrade = models.BooleanField("было изменено вручную", default=False)
    check_document_upgrade = models.BooleanField("было изменено вручную", default=False)
    check_property_upgrade = models.BooleanField("было изменено вручную", default=False)
    data_create = models.DateField(default=timezone.now, verbose_name="Дата добавления")

    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))
    autosave_tag = models.BooleanField("автоматическая загрузка", default=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"Арт.мотрум: {self.article} | Арт.поставщика: {self.article_supplier} | Название товара: {self.name}"

    def save(self, *args, **kwargs):
        # если товара нет бд сделать артикул
        if self.article == "":
            article = create_article_motrum(self.supplier.id)
            self.article = article
        # получение категорий мотрум из категорий поставщика
        filter_catalog = get_motrum_category(self)
        
        if self.category == None:
            self.category = filter_catalog[0]
        if self.group == None:
            self.group = filter_catalog[1]
        # добавление производителя из групп вендора если нет своего
        if self.vendor == None:
            if self.group_supplier.vendor != None:
                vendor = self.group_supplier.vendor
                
        super().save(*args, **kwargs)

        # обновление цен товаро потому что могли змеиться группы для скидки
        price = Price.objects.filter(prod=self.id)
        for price_one in price:
            price_one.price_supplier = price_one.price_supplier
            price_one.save()

    # удаление пустых исторических записей
    @receiver(post_create_historical_record)
    def post_create_historical_record_callback(
        sender, instance, history_instance, **kwargs
    ):
        if history_instance.history_type == "~":
            delta = history_instance.diff_against(history_instance.prev_record)
            if delta.changed_fields == []:
                history_instance.delete()


# @receiver(post_save, sender=Product)
# def update_change_reason(sender, instance, **kwargs):
#     print(instance)
#     # if instance._change_reason == None:
#     update_change_reason(instance, 'Автоматическое')


class CategoryProduct(models.Model):
    name = models.CharField("Название категории", max_length=50)
    slug = models.SlugField(null=True)
    article_name = models.CharField(
        "Артикул категории",
        max_length=25,
        blank=True,
        null=True,
    )
    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        slug_text = self.name
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)
        super().save(*args, **kwargs)


class GroupProduct(models.Model):
    name = models.CharField("Название группы", max_length=50)
    slug = models.SlugField(null=True)
    category = models.ForeignKey(
        CategoryProduct,
        verbose_name="категория",
        on_delete=models.PROTECT,
    )
    article_name = models.CharField(
        "Артикул категории",
        max_length=25,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Группа товара"
        verbose_name_plural = "Группы товаров"

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        slug_text = self.name
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)
        super().save(*args, **kwargs)


class Price(models.Model):
    prod = models.OneToOneField(
        Product,
        related_name="price",
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
        # blank=True,
        null=True,
    )

    vat_include = models.BooleanField("Включен ли налог в цену", default=True)

    price_supplier = models.FloatField(
        "Цена в каталоге поставщика в валюте каталога",
        # blank=True,
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

    extra_price = models.BooleanField("Цена по запросу", default=False)

    sale = models.ForeignKey(
        Discount,
        verbose_name="Примененная скидка",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    class Meta:
        verbose_name = "Цена"
        verbose_name_plural = "Цены"

    def __str__(self):
        return f"Цена поставщика:{self.rub_price_supplier} ₽ Цена мотрум: {self.price_motrum} ₽"

    def save(self, *args, **kwargs):
        # если 0 цена или экстра прайс проставить нули и теги
        if self.price_supplier == 0 or self.extra_price == True:
            self.extra_price = True
            self.price_supplier = 0
            self.rub_price_supplier = 0
            self.price_motrum = 0
       
        #  если цена есть
        elif self.price_supplier != 0:
            self.extra_price == False

            rub_price_supplier = get_price_supplier_rub(
                self.currency.words_code,
                self.vat.name,
                self.vat_include,
                self.price_supplier,
            )
            self.rub_price_supplier = rub_price_supplier

            price_motrum_all = get_price_motrum(
                self.prod.category_supplier,
                self.prod.group_supplier,
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
        related_name="historic_stock",
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

    to_order = models.BooleanField("Товар под заказ", default=False)
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    class Meta:
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"

    def __str__(self):
        return f"{self.stock_supplier} {self.stock_supplier}"

    def save(self, *args, **kwargs):

        lots = get_lot(self.lot.name, self.stock_supplier, self.lot_complect)

        self.stock_supplier_unit = lots[1]
        self.lot_complect = lots[2]
        
        name1 = super().save(*args, **kwargs)


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
    link = models.CharField("ссылка у поставщика", max_length=150)
    hide = models.BooleanField("скрыть", default=False)

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    # def __str__(self):
    #     return None
    # return mark_safe(
    #     '<img src="{}{}" height="200" width="200" />'.format(MEDIA_URL, self.photo)
    # )

    # def delete(self, *args, **kwargs):
    #     self.hide = True
    #     super().save(*args, **kwargs)  # Call the "real" save() method.


class ProductDocument(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    document = models.FileField(
        "Документ", upload_to=get_file_path_add, max_length=255, null=True
    )
    # file = models.CharField("фаил в системе", max_length=100, null=True)
    # type_doc = models.CharField("Тип документации", max_length=150, null=True)
    type_doc = models.CharField(
        "Тип документации", max_length=100, choices=TYPE_DOCUMENT, default="Other"
    )
    name = models.CharField("Название документа", max_length=255, null=True)
    link = models.CharField("ссылка у поставщика", max_length=255, null=True)
    hide = models.BooleanField("скрыть", default=False)
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    class Meta:
        verbose_name = "Документация"
        verbose_name_plural = "Документации"

    def __str__(self):
        return f"{self.document}"


class ProductProperty(models.Model):
    product = models.ForeignKey(
        Product,
        # related_name="historic_property",
        on_delete=CASCADE,
    )
    
    name = models.CharField("название", max_length=600)
    value = models.CharField("значение", max_length=600)
    unit_measure = models.CharField("значение", max_length=600, null=True)
    hide = models.BooleanField("Удалить", default=False)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Характеристика \свойства"
        verbose_name_plural = "Характеристики\свойства"

    def __str__(self):
        return f"{self.name}:{self.value}"
