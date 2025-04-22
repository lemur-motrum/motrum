import os
import re
import traceback
from django.contrib.postgres.indexes import GinIndex
from django.urls import reverse
from django.utils import timezone
from django.db import models
from django.db.models.deletion import CASCADE
from django.dispatch import receiver

from apps.logs.utils import error_alert
from simple_history.models import HistoricalRecords


from apps.core.models import Currency, Vat
from apps.core.utils import (
    create_article_motrum,
    get_file_path_add,
    get_lot,
    get_motrum_category,
    get_price_motrum,
    get_price_supplier_rub,
)
from simple_history.signals import (
    post_create_historical_record,
)
from apps.core.utils_web import get_file_path_catalog_web
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
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.user.models import AdminUser


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

    article = models.CharField("Артикул мотрум", max_length=500, blank=False)
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="Поставщик",
        on_delete=models.PROTECT,
    )
    vendor = models.ForeignKey(
        Vendor,
        verbose_name="Производитель",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    article_supplier = models.CharField("Артикул поставщика", max_length=500)
    additional_article_supplier = models.CharField(
        "Дополнительный артикул поставщика", max_length=500, blank=True, null=True
    )
    category_supplier_all = models.ForeignKey(
        SupplierCategoryProductAll,
        verbose_name="Подгруппа категории товара от поставщиков",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    group_supplier = models.ForeignKey(
        SupplierGroupProduct,
        verbose_name="Группа товара от поставщиков",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    category_supplier = models.ForeignKey(
        SupplierCategoryProduct,
        verbose_name="Категории товара от поставщиков",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        "CategoryProduct",
        verbose_name="Категория Мотрум",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    group = models.ForeignKey(
        "GroupProduct",
        verbose_name="Группа Мотрум",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    description = models.CharField(
        "Описание товара", max_length=4000, blank=True, null=True
    )
    name = models.CharField("Название товара", max_length=600)
    slug = models.SlugField(null=True, max_length=600)
    data_create = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    # data_update = models.DateField(default=timezone.now, verbose_name="Дата обновления")
    data_update = models.DateField(auto_now=True, verbose_name="Дата обновления")
    check_to_order = models.BooleanField("Доступность к заказу", default=True)
    promote = models.BooleanField("Продвижение на главной в слайдере", default=False)

    autosave_tag = models.BooleanField("Автоматическая загрузка", default=True)
    add_in_nomenclature = models.BooleanField("Загружен из номенклатуры", default=False)
    # in_auto_sale = models.BooleanField("Разрешить применять скидки автоматичсеки", default=False)
    in_view_website = models.BooleanField("Видимость на сайте", default=True)
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        

    def __str__(self):
        return f"Арт.мотрум: {self.article} | Арт.поставщика: {self.article_supplier} | Название товара: {self.name}"

    def save(self, *args, **kwargs):

        if self.id is None:
            pass
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
        # # добавление производителя из групп вендора если нет своего
        # if self.vendor == None:
        #     if self.category_supplier_all is not None:
        #         if self.category_supplier_all.vendor is not None:
        #             self.vendor = self.category_supplier_all.vendor

        #     elif self.group_supplier is not None:
        #         if self.group_supplier.vendor is not None:
        #             self.vendor = self.group_supplier.vendor
        #     print(self.vendor)

        # удалить лишние пробелы
        if self.description != None:
            self.description = self.description.strip()
            self.description = " ".join(self.description.split())
        try:
            if self.slug == None:
                slug_text = f"{self.name}-{self.article}"
                regex = r"[^A-Za-z0-9,А-ЯЁа-яё, ,-.]"
                slugish = re.sub(regex, "", slug_text)
                slugish = translit.translify(slugish)
                self.slug = slugify(slugish)

        except Exception as e:
            print(e)
            error = "file_error"
            location = "Обновление слагов"
            info = f"Обновление слагов"
            e = error_alert(error, location, info)

        super().save(*args, **kwargs)

        # обновление цен товаров потому что могли заменить группы для скидки
        try:
            price = Price.objects.get(prod=self.id)
            price.price_supplier = price.price_supplier
            price.save()
        except Price.DoesNotExist:
            pass

    def get_absolute_url(self):
        if self.category is not None:
            if self.group is not None:
                return reverse(
                    "product:product_one",
                    kwargs={
                        "category": self.category.slug,
                        "group": self.group.slug,
                        "article": self.article,
                    },
                )
            else:
                return reverse(
                    "product:product_one_without_group",
                    kwargs={
                        "category": self.category.slug,
                        "article": self.article,
                    },
                )
        else:
            return reverse(
                "product:product_one_without_group",
                kwargs={
                    "category": "other",
                    "article": self.article,
                },
            )

    def get_url_document(self):
        if self.category is not None:
            category = self.category.slug
        else:
            category = "other"

        if self.group is not None:

            groupe = self.group.slug
        else:
            groupe = "none_group"

        product = str(self.article)

        url = "{0}/{1}/{2}/{3}".format(
            "product",
            category,
            groupe,
            product,
        )
        return url

    def get_url_document_test(self):

        product = int(self.article)

        url = "{0}/{1}".format(
            "product",
            product,
        )
        return url

    def get_presale_discount(self):
        from apps.supplier.models import Discount

        supplier = self.supplier
        try:
            discount = Discount.objects.get(supplier=supplier, is_tag_pre_sale=True)
            return discount.percent
        except Discount.DoesNotExist:
            return False

    # def get_blank(self, Model, product_blank):
    #         # item = Product.objects.filter(id=self.id).values()
    #         item = list(self)
    #         product_blank_local = ""
    #         for product_item in item:
    #             product_blank_dict = {
    #                 k: v for k, v in product_item.items() if v == None
    #             }

    #             for item_dict in product_blank_dict:
    #                 verbose_name = self._meta.get_field(item_dict).verbose_name
    #                 if (
    #                     verbose_name != "Подгруппа категории товара от поставщиков"
    #                     and verbose_name != "Группа товара от поставщиков"
    #                     and verbose_name != "Группа Мотрум"
    #                     and verbose_name != "Дополнительный артикул поставщика"
    #                 ):
    #                     if verbose_name == "Категория Мотрум":
    #                         item_one = f"<li font-size: 0.6rem>Группировка Motrum</li>"
    #                     elif verbose_name == "Категории товара от поставщиков":
    #                         item_one = (
    #                             f"<li font-size: 0.6rem>Группировка поставщика</li>"
    #                         )
    #                     else:
    #                         item_one = f"<li font-size: 0.6rem>{verbose_name}</li>"
    #                     product_blank_local = f"{product_blank_local}{item_one}"

    #         product_blank = f"{product_blank}{product_blank_local}"
    #         return product_blank

    # удаление пустых исторических записей
    @receiver(post_create_historical_record)
    def post_create_historical_record_callback(
        sender, instance, history_instance, **kwargs
    ):
        if history_instance.history_type == "~":
            delta = history_instance.diff_against(history_instance.prev_record)
            if delta.changed_fields == []:
                history_instance.delete()


@receiver(post_save, sender=Product)
def add_logs_created(sender, instance, created, **kwargs):
    from apps.logs.models import LogsAddProduct

    if created:
        log = LogsAddProduct.objects.create(product=instance)
        print(f"New deal with pk: {instance.pk} was created.")


class CategoryProduct(models.Model):
    name = models.CharField("Название категории", max_length=500)
    slug = models.SlugField(null=True, max_length=500)
    article_name = models.CharField(
        "Артикул категории",
        max_length=25,
        blank=True,
        null=True,
    )
    image = models.ImageField(
        "Изображение категории", upload_to=get_file_path_catalog_web, null=True
    )
    is_view_home_web = models.BooleanField(
        "Отображение на главной сайта", default=False
    )
    is_send_email = models.BooleanField("Отображение в емаил рассылке", default=False)
    article_home_web = models.PositiveIntegerField(
        "Очередность вывода на главную",
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

    def get_absolute_url(self):

        return reverse(
            "product:group",
            kwargs={
                "category": self.slug,
            },
        )


class GroupProduct(models.Model):
    name = models.CharField("Название группы", max_length=500)
    slug = models.SlugField(null=True, max_length=500)
    category = models.ForeignKey(
        CategoryProduct,
        verbose_name="Категория Мотрум",
        on_delete=models.PROTECT,
    )
    article_name = models.CharField(
        "Артикул категории",
        max_length=25,
        blank=True,
        null=True,
    )
    image = models.ImageField(
        "Изображение категории", upload_to=get_file_path_catalog_web, null=True
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
        verbose_name="Продукт",
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
        blank=True,
        null=True,
        default=0,
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
    in_auto_sale = models.BooleanField(
        "Разрешить применять скидки автоматически", default=True
    )
    data_update = models.DateField(auto_now=True, verbose_name="Дата обновления")
    # data_update = models.DateField(default=timezone.now, verbose_name="Дата обновления")

    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    class Meta:
        verbose_name = "Цена"
        verbose_name_plural = "Цены"

    def __str__(self):
        return f"Цена поставщика:{self.rub_price_supplier} ₽ Цена мотрум: {self.price_motrum} ₽"

    def save(self, *args, **kwargs):
        print("SAVE PRICE")
        # если 0 цена или экстра прайс проставить нули и теги
        if (
            self.price_supplier == 0
            or self.extra_price == True
            or self.price_supplier == None
        ):
            self.extra_price = True
            self.price_supplier = None
            self.rub_price_supplier = None
            self.price_motrum = None

        #  если цена есть
        elif self.price_supplier != 0:
            self.extra_price == False

            # получить рублевую цену
            rub_price_supplier = get_price_supplier_rub(
                self.currency.words_code,
                self.vat.name,
                self.vat_include,
                self.price_supplier,
            )
            self.rub_price_supplier = rub_price_supplier

        # получить скидки
        if self.in_auto_sale:
            price_motrum_all = get_price_motrum(
                self.prod.category_supplier,
                self.prod.group_supplier,
                self.prod.vendor,
                self.rub_price_supplier,
                self.prod.category_supplier_all,
                self.prod.supplier,
            )

            price_motrum = price_motrum_all[0]
            sale = price_motrum_all[1]
            if self.price_motrum:
                self.price_motrum = self.price_motrum
            else:
                self.price_motrum = price_motrum

            self.sale = sale
        else:
            self.price_motrum = self.rub_price_supplier
        print("stop save price")
        super().save(*args, **kwargs)

    # def price_sale_personal(self):
    #     from apps.client.models import Client
    #     print(123123)
    #     request = RequestMiddleware(get_response=None)
    #     request = request.thread_local.current_request
    #     print(request.user)

    #     if request.user.is_authenticated :
    #         print(33333)
    #         if request.user.is_staff == False:
    #             client = Client.objects.get(id=request.user.id)
    #             discount = client.percent

    #             price = self.rub_price_supplier

    #             price_discount = price - (price / 100 * float(discount))

    #             return round(price_discount, 2)
    #         else:
    #             return self.rub_price_supplier
    #     else:
    #         print(22222)
    #         return self.rub_price_supplier

    def get_sale_price_motrum(self):
        from apps.supplier.models import (
            Discount,
        )

        item_category = self.prod.category_supplier
        item_group = self.prod.group_supplier
        vendors = self.prod.vendor
        rub_price_supplier = self.rub_price_supplier
        all_item_group = self.prod.category_supplier_all
        supplier = self.prod.supplier

        motrum_price = rub_price_supplier
        percent = 0
        sale = [None]

        # получение процента функция
        def get_percent(item):
            for i in item:
                return i.percent

        if all_item_group and percent == 0:
            discount_all_group = Discount.objects.filter(
                category_supplier_all=all_item_group.id,
                is_tag_pre_sale=False,
            )

            if discount_all_group:
                percent = get_percent(discount_all_group)
                sale = discount_all_group

            # скидка по группе

        if item_group and percent == 0:

            discount_group = Discount.objects.filter(
                category_supplier_all__isnull=True,
                group_supplier=item_group.id,
                is_tag_pre_sale=False,
            )

            if discount_group:
                percent = get_percent(discount_group)
                sale = discount_group

                # if percent != 0

        # скидка по категории
        if item_category and percent == 0:

            discount_categ = Discount.objects.filter(
                category_supplier_all__isnull=True,
                group_supplier__isnull=True,
                category_supplier=item_category.id,
                is_tag_pre_sale=False,
            )

            if discount_categ:
                percent = get_percent(discount_categ)
                sale = discount_categ

        if vendors and percent == 0:

            discount_all = Discount.objects.filter(
                vendor=vendors,
                group_supplier__isnull=True,
                category_supplier__isnull=True,
                category_supplier_all__isnull=True,
                is_tag_pre_sale=False,
            )
            # скидка по всем вендору
            if discount_all:
                percent = get_percent(discount_all)
                sale = discount_all

        if percent == 0:

            discount_all = Discount.objects.filter(
                supplier=supplier,
                vendor__isnull=True,
                group_supplier__isnull=True,
                category_supplier__isnull=True,
                category_supplier_all__isnull=True,
                is_tag_pre_sale=False,
            )
            # скидка по всем вендору
            if discount_all:
                percent = get_percent(discount_all)
                sale = discount_all
            # нет скидки

        # motrum_price = rub_price_supplier - (rub_price_supplier / 100 * float(percent))
        # # обрезать цены
        # motrum_price = round(motrum_price, 2)
        if sale[0]:
            return sale[0].percent
        else:
            return None


# курсы валют
class CurrencyRate(models.Model):
    currency = models.ForeignKey(
        Currency,
        on_delete=models.CASCADE,
    )

    date = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    value = models.FloatField("Курс ЦБ", blank=True, null=True)
    vunit_rate = models.FloatField("Курс ЦБ за единицу", blank=True, null=True)
    count = models.PositiveIntegerField("Единиц", blank=True, null=True)


class Stock(models.Model):
    prod = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        # blank=True,
        null=True,
    )
    lot = models.ForeignKey(
        "Lot",
        verbose_name="Единица измерения поставщика",
        on_delete=models.PROTECT,
    )
    stock_supplier = models.PositiveIntegerField(
        "Остаток на складе поставщика в единицах поставщика",
        blank=True,
        null=True,
    )
    lot_complect = models.PositiveIntegerField(
        "Содержание набора (комплекта) в штуках", default=1
    )
    stock_supplier_unit = models.PositiveIntegerField(
        "Остаток на складе поставщика в штуках",
        null=True,
    )
    stock_motrum = models.PositiveIntegerField(
        "Остаток на складе Motrum в штуках", default=0
    )
    stock_motrum_reserve = models.PositiveIntegerField(
        "Резерв на складе Motrum в штуках", default=0
    )
    to_order = models.BooleanField("Товар под заказ", default=False)
    data_update = models.DateField(
        auto_now=True, verbose_name="Дата обновления поставщика"
    )
    data_update_motrum = models.DateField(
        auto_now=True, verbose_name="Дата обновления motrum"
    )
    transit_count = models.PositiveIntegerField(
        "Ближайшая поставка количество", blank=True, null=True
    )
    data_transit = models.DateField(
        verbose_name="Ближайшая поставка дата", blank=True, null=True
    )
    order_multiplicity = models.PositiveIntegerField(
        "Коэффициент кратности заказа", default=1
    )
    is_one_sale = models.BooleanField("Разрешение продавать поштучно", default=True)

    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    class Meta:
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"

    def __str__(self):
        return f"{self.stock_supplier} {self.stock_supplier}"

    def save(self, *args, **kwargs):
        if self.lot_complect == 0:
            self.lot_complect = 1

        if self.lot_complect == None:
            self.lot_complect = 1

        print(self.stock_supplier_unit)  # посчитать комплекты лотов
        if self.stock_supplier != None and self.stock_supplier_unit == None:

            lots = get_lot(self.lot.name, self.stock_supplier, self.lot_complect)
            self.stock_supplier_unit = lots[1]
            self.lot_complect = lots[2]

        if self.stock_supplier != None and self.stock_supplier != 0:

            lots = get_lot(self.lot.name, self.stock_supplier, self.lot_complect)
            self.stock_supplier_unit = lots[1]
            self.lot_complect = lots[2]

        super().save(*args, **kwargs)


class Lot(models.Model):
    name = models.CharField("Полное название", max_length=30)
    name_shorts = models.CharField("Короткое название", max_length=6, null=True)
    slug = models.SlugField(null=True, max_length=30)

    class Meta:
        verbose_name = "Единица измерения поставщика"
        verbose_name_plural = "Единицы измерений поставщиков"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug_text = self.name
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)

        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        # on_delete=models.PROTECT,
    )
    photo = models.ImageField("Изображение", upload_to=get_file_path_add,max_length=500, null=True)
    # file = models.CharField("фаил в системе", max_length=100, null=True)
    link = models.CharField("Ссылка у поставщика", max_length=250)
    hide = models.BooleanField("Скрыть", default=False)
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    class Meta:
        ordering = ["pk"]
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     product = self.product
    #     product.save


class ProductDocument(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
    )
    document = models.FileField(
        "Документ", upload_to=get_file_path_add, max_length=255, null=True
    )
    type_doc = models.CharField(
        "Тип документации", max_length=100, choices=TYPE_DOCUMENT, default="Other"
    )
    name = models.CharField("Название документа", max_length=255, null=True)
    link = models.CharField("Ссылка у поставщика", max_length=255, null=True)
    hide = models.BooleanField("Скрыть", default=False)

    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    class Meta:
        verbose_name = "Документация"
        verbose_name_plural = "Документации"

    def __str__(self):
        return f"{self.document}"

    def extension(self):
        name, extension = os.path.splitext(self.document.name)
        extension = extension.replace(".", "")
        return extension

    # def pre_save(self, model_instance, add):
    #     file = super().pre_save(model_instance, add)
    #     if file and not file._committed:
    #         print(7676767666666666666)
    #         # Commit the file to storage prior to saving the model
    #         file.save(file.name, file.file, save=False)
    #     return file

    # def save(self, *args, **kwargs):
    #     # self.document
    #     super().save(*args, **kwargs)


class ProductProperty(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=CASCADE,
    )

    name = models.CharField("Название", max_length=600)
    value = models.CharField("Значение", max_length=600)
    unit_measure = models.CharField("Короткое имя значения", max_length=600, null=True)
    hide = models.BooleanField("Удалить", default=False)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Характеристика\свойства"
        verbose_name_plural = "Характеристики\свойства"

    def __str__(self):
        return f"{self.name}:{self.value}"

    def save(self, *args, **kwargs):
        if self.value == "true" or self.value == "True":
            self.value == "Да"

        if self.value == "false" or self.value == "False":
            self.value == "Нет"
        super().save(*args, **kwargs)


class Cart(models.Model):
    from apps.client.models import Client

    client = models.ForeignKey(
        Client, verbose_name="Клиент", on_delete=models.PROTECT, blank=True, null=True
    )
    is_active = models.BooleanField("корзина сохранена", default=False)
    session_key = models.CharField(max_length=500, blank=True, null=True)
    cart_admin = models.ForeignKey(
        AdminUser,
        on_delete=models.PROTECT,
        verbose_name="Администратор",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return str(self.id)

    @classmethod
    def create_cart_admin(cls, session, admin):
        cart = cls.objects.create(
            session_key=None, is_active=False, client=None, cart_admin=admin
        )

        return cart


TAG_DOC = (
    ("ONE", "Один вариант"),
    ("MULTI", "Несколько вариантов"),
    ("NONE", "Нет варинтов"),
    ("-", "Не из документа"),
)


class ProductCart(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        verbose_name="Продукты",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    product_price = models.FloatField(
        "Цена товара",
        blank=True,
        null=True,
        default=None,
    )
    product_price_motrum = models.FloatField(
        "Цена товара",
        blank=True,
        null=True,
        default=None,
    )
    product_sale_motrum = models.FloatField(
        "Скидка мотрум товара ",
        blank=True,
        null=True,
        default=None,
    )
    sale_client = models.FloatField(
        "Скидка клиента из парсинга фаила",
        blank=True,
        null=True,
        default=None,
    )
    vendor = models.ForeignKey(
        Vendor,
        verbose_name="Производитель",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="Поставщик",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    product_new = models.CharField(
        "Название товара нового без добавления в бд",
        default=None,
        max_length=500,
        blank=True,
        null=True,
    )

    product_new_article = models.CharField(
        "Артикул товара нового без добавления в бд",
        default=None,
        max_length=500,
        blank=True,
        null=True,
    )
    product_new_price = models.FloatField(
        "Цена товара нового без добавления в бд",
        blank=True,
        null=True,
        default=None,
    )
    product_new_sale = models.FloatField(
        "Доп.скидка товара нового без добавления в бд",
        blank=True,
        null=True,
        default=None,
    )
    product_new_sale_motrum = models.FloatField(
        "Скидка мотрум товара нового без добавления в бд",
        blank=True,
        null=True,
        default=None,
    )

    quantity = models.IntegerField(
        "количество товара",
        blank=True,
        null=True,
    )
    comment = models.CharField(
        "Комментарий",
        default=None,
        max_length=1000,
        blank=True,
        null=True,
    )
    date_delivery = models.DateField(verbose_name="Дата поставки товара", null=True)
    tag_auto_document = models.CharField(max_length=100, choices=TAG_DOC, default="-")

    class Meta:
        verbose_name = "Корзина продукт"
        verbose_name_plural = "Корзина Продукты"

    def __str__(self):
        return str(self.id)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
