from email.policy import default
import os
from pyexpat import model
from django.utils import timezone
from django.db import models
from simple_history import register

from apps import core
from apps.core.models import Currency, Vat

from simple_history.models import HistoricalRecords, HistoricForeignKey

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

class RoutableModel(models.Model):

    
    class Meta:
        abstract = True
        
class Product(models.Model):
    article = models.PositiveIntegerField("Артикул мотрум", blank=False)
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

    history = HistoricalRecords(bases=[RoutableModel])
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return f"Арт.мотрум: {self.article} | Арт.поставщика: {self.article_supplier} | Название товара: {self.name}"

    def save(self, *args, **kwargs):
        if self.article == None:
            article = create_article_motrum(self.supplier, self.vendor)
            self.article = article
        super().save(*args, **kwargs)
        # обновление цен товаров
        # price = Price.objects.filter(prod=self.id)
        # for price_one in price:
        #     price_one.price_supplier = price_one.price_supplier
        #     price_one.save()

class CategoryProduct(models.Model):
    name = models.CharField("Название категории", max_length=50)

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return self.name


class GroupProduct(models.Model):
    name = models.CharField("Название группы", max_length=50)
    article_name = models.CharField("Артикул группы", max_length=25, blank=True, null=True)
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

class TestOrganizationWithHistory(models.Model):
    name = models.CharField(max_length=15, unique=True)
    history = HistoricalRecords()
    
class TestHistoricParticipanToHistoricOrganization(models.Model):
    """
    Historic table foreign key to historic table.

    In this case as_of queries on the origin model (this one)
    or on the target model (the other one) will traverse the
    foreign key relationship honoring the timepoint of the
    original query.  This only happens when both tables involved
    are historic.

    NOTE: related_name has to be different than the one used in
          TestParticipantToHistoricOrganization as they are
          sharing the same target table.
    """

    name = models.CharField(max_length=15, unique=True)
    organization = Price(
        TestOrganizationWithHistory,
        on_delete=CASCADE,
        related_name="historic_participants",
    )
    history = HistoricalRecords()
    
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
    history = HistoricalRecords(bases=[RoutableModel])
    class Meta:
        verbose_name = "Цена"
        verbose_name_plural = "Цены"

    def __str__(self):
        return f"{self.rub_price_supplier} {self.price_motrum}"

    def save(self, *args, **kwargs):
    
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

    def test_historic_to_historic(self):
        """
        Historic table foreign key to historic table.

        In this case as_of queries on the origin model (this one)
        or on the target model (the other one) will traverse the
        foreign key relationship honoring the timepoint of the
        original query.  This only happens when both tables involved
        are historic.

        At t1 we have one org, one participant.
        At t2 we have one org, two participants, however the org's name has changed.
        At t3 we have one org, and one participant has left.
        """
        org = Product.objects.create(name="original")
        p1 = TestHistoricParticipanToHistoricOrganization.objects.create(
            name="p1", organization=org
        )
        t1_one_participant = timezone.now()
        p2 = TestHistoricParticipanToHistoricOrganization.objects.create(
            name="p2", organization=org
        )
        org.name = "modified"
        org.save()
        t2_two_participants = timezone.now()
        p1.delete()
        t3_one_participant = timezone.now()

        # forward relationships - see how natural chasing timepoint relations is
        p1t1 = TestHistoricParticipanToHistoricOrganization.history.as_of(
            t1_one_participant
        ).get(name="p1")
        self.assertEqual(p1t1.organization, org)
        self.assertEqual(p1t1.organization.name, "original")
        p1t2 = TestHistoricParticipanToHistoricOrganization.history.as_of(
            t2_two_participants
        ).get(name="p1")
        self.assertEqual(p1t2.organization, org)
        self.assertEqual(p1t2.organization.name, "modified")
        p2t2 = TestHistoricParticipanToHistoricOrganization.history.as_of(
            t2_two_participants
        ).get(name="p2")
        self.assertEqual(p2t2.organization, org)
        self.assertEqual(p2t2.organization.name, "modified")
        p2t3 = TestHistoricParticipanToHistoricOrganization.history.as_of(
            t3_one_participant
        ).get(name="p2")
        self.assertEqual(p2t3.organization, org)
        self.assertEqual(p2t3.organization.name, "modified")

        # reverse relationships
        # at t1
        ot1 = TestOrganizationWithHistory.history.as_of(t1_one_participant).all()[0]
        self.assertEqual(ot1.historic_participants.count(), 1)
        self.assertEqual(ot1.historic_participants.all()[0].name, p1.name)
        # at t2
        ot2 = TestOrganizationWithHistory.history.as_of(t2_two_participants).all()[0]
        self.assertEqual(ot2.historic_participants.count(), 2)
        self.assertIn(p1.name, [item.name for item in ot2.historic_participants.all()])
        self.assertIn(p2.name, [item.name for item in ot2.historic_participants.all()])
        # at t3
        ot3 = TestOrganizationWithHistory.history.as_of(t3_one_participant).all()[0]
        self.assertEqual(ot3.historic_participants.count(), 1)
        self.assertEqual(ot3.historic_participants.all()[0].name, p2.name)
        # current
        self.assertEqual(org.historic_participants.count(), 1)
        self.assertEqual(org.historic_participants.all()[0].name, p2.name)

        self.assertTrue(is_historic(ot1))
        self.assertFalse(is_historic(org))

        self.assertIsInstance(
            to_historic(ot1), TestOrganizationWithHistory.history.model
        )
        self.assertIsNone(to_historic(org))

        # test querying directly from the history table and converting
        # to an instance, it should chase the foreign key properly
        # in this case if _as_of is not present we use the history_date
        # https://github.com/jazzband/django-simple-history/issues/983
        pt1h = TestHistoricParticipanToHistoricOrganization.history.all()[0]
        pt1i = pt1h.instance
        self.assertEqual(pt1i.organization.name, "modified")
        pt1h = TestHistoricParticipanToHistoricOrganization.history.all().order_by(
            "history_date"
        )[0]
        pt1i = pt1h.instance
        self.assertEqual(pt1i.organization.name, "original")


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
    history = HistoricalRecords()
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
    type_doc = models.CharField(
        "Тип документации", max_length=40, choices=TYPE_DOCUMENT, default="Other"
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
