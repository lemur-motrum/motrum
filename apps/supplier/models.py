from django.db import models
from django.utils.text import slugify
from pytils import translit
import threading
from simple_history.utils import update_change_reason

from apps.core.models import Currency, Vat
from apps.core.utils import get_file_price_path_add


# Create your models here.


class Supplier(models.Model):

    name = models.CharField("Название поставщика", max_length=40)
    slug = models.SlugField(null=True, max_length=40)
    file = models.FileField(
        "Архив с прайсами",
        upload_to=get_file_price_path_add,
        max_length=255,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        slug_text = self.name
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)
        super().save(*args, **kwargs)


class Vendor(models.Model):

    name = models.CharField("Название производителя", max_length=40)
    slug = models.SlugField(null=True, max_length=40)
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


class SupplierCategoryProduct(models.Model):
    name = models.CharField("Название категории", max_length=150)
    slug = models.CharField(
        max_length=150,
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
    vendor = models.ForeignKey(
        Vendor,
        verbose_name="Вендор",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    article_name = models.CharField(
        "Артикул категории",
        max_length=25,
        blank=True,
        null=True,
    )
    category_catalog = models.ForeignKey(
        "product.CategoryProduct",
        verbose_name="Категория каталога мотрум",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    group_catalog = models.ForeignKey(
        "product.GroupProduct",
        verbose_name="Группа каталога мотрум",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    autosave_tag = models.BooleanField("Автоматическая загрузка", default=True)

    class Meta:
        verbose_name = "Категория товара у поставщика"
        verbose_name_plural = "Категории товаров у поставщика"

    def __str__(self):
        if self.article_name:
            return f"{self.article_name}{self.name}"
        else:
            return f"{self.name}"

    def save(self, *args, **kwargs):
        if self.slug == None:
            slug_text = self.name
            slugish = translit.translify(slug_text)
            self.slug = slugify(slugish)

       
        super().save(*args, **kwargs)
        from apps.product.models import Product

        # обновление категорий связанных продукты
        product = Product.objects.filter(category_supplier=self.id)
     
        def background_task():
            # Долгосрочная фоновая задача
            for product_one in product:
                product_one.category = self.category_catalog
                if self.group_catalog:
                    product_one.group = self.group_catalog
                print(product_one)
              
                product_one.save()
                update_change_reason(product_one, "Автоматическое")

        daemon_thread = threading.Thread(target=background_task)
        daemon_thread.setDaemon(True)
        daemon_thread.start()


class SupplierGroupProduct(models.Model):
    name = models.CharField("Название группы", max_length=150)
    slug = models.CharField(
        max_length=150,
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
    vendor = models.ForeignKey(
        Vendor,
        verbose_name="Вендор",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    article_name = models.CharField(
        "Артикул группы",
        max_length=25,
        blank=True,
        null=True,
    )
    category_supplier = models.ForeignKey(
        SupplierCategoryProduct,
        verbose_name="Категория поставщика",
        on_delete=models.PROTECT,
    )
    category_catalog = models.ForeignKey(
        "product.CategoryProduct",
        verbose_name="Категория каталога мотрум",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    group_catalog = models.ForeignKey(
        "product.GroupProduct",
        verbose_name="Группа каталога мотрум",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    autosave_tag = models.BooleanField("Автоматическая загрузка", default=True)

    class Meta:
        verbose_name = "Группа товара у поставщика"
        verbose_name_plural = "Группы товаров у поставщика"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from apps.product.models import Product

        # обновление категорий связанных продукты
        product = Product.objects.filter(group_supplier=self.id)

        def background_task():
            # Долгосрочная фоновая задача
            for product_one in product:
                product_one.category = self.category_catalog
                if self.group_catalog:
                    product_one.group = self.group_catalog
                    
                # добавление производителя из групп вендора если нет своего для дельта и оптимус
                if (
                    product_one.supplier.slug == "delta"
                    or product_one.supplier.slug == "optimus-drive"
                ):
                    if product_one.group_supplier is not None:
                        if product_one.group_supplier.vendor is not None:
                            product_one.vendor = product_one.group_supplier.vendor
                    

                product_one.save()
                update_change_reason(product_one, "Автоматически из групп поставщика")

        daemon_thread = threading.Thread(target=background_task)
        daemon_thread.setDaemon(True)
        daemon_thread.start()

        # for product_one in product:
        #     product_one.category = self.category_catalog
        #     if self.group_catalog:
        #         product_one.group = self.group_catalog

        #     product_one.save()


class SupplierCategoryProductAll(models.Model):
    name = models.CharField("Название категории", max_length=150)
    slug = models.CharField(
        "слаг",
        max_length=150,
        blank=True,
        null=True,
    )
    article_name = models.CharField(
        "Артикул категории",
        max_length=55,
        blank=True,
        null=True,
    )
    supplier = models.ForeignKey(
        Supplier,
        verbose_name="Поставщик",
        on_delete=models.PROTECT,
    )
    vendor = models.ForeignKey(
        Vendor,
        verbose_name="Вендор",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    category_supplier = models.ForeignKey(
        SupplierCategoryProduct,
        verbose_name="Категория каталога поставщика",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    group_supplier = models.ForeignKey(
        SupplierGroupProduct,
        verbose_name="Группа каталога поставщика",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    category_catalog = models.ForeignKey(
        "product.CategoryProduct",
        verbose_name="Категория каталога мотрум",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    group_catalog = models.ForeignKey(
        "product.GroupProduct",
        verbose_name="Группа каталога мотрум",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    autosave_tag = models.BooleanField("автоматическая загрузка", default=True)

    class Meta:
        verbose_name = "Подгруппы поставщиков"
        verbose_name_plural = "Подгруппы поставщиков"

    def __str__(self):

        return f"{self.name} {self.article_name}| Поставщик:{self.supplier} Вендор:{self.vendor}"

    # {self.article_name}| Поставщик:{self.supplier} Вендор:{self.vendor}
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from apps.product.models import Product

        # обоновление категорйи связанных продуктов
        product = Product.objects.filter(category_supplier_all=self.id)

        def background_task():
            # Долгосрочная фоновая задача
            for product_one in product:
                product_one.category = self.category_catalog
                if self.group_catalog:
                    product_one.group = self.group_catalog
                    # update_change_reason(product_one, "Автоматическое")

                product_one.save()
                update_change_reason(product_one, "Автоматическое")

        daemon_thread = threading.Thread(target=background_task)
        daemon_thread.setDaemon(True)
        daemon_thread.start()

        # for product_one in product:
        #     product_one.category = self.category_catalog
        #     if self.group_catalog:
        #         product_one.group = self.group_catalog

        #     product_one.save()


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
        blank=True,
        null=True,
    )

    category_supplier = models.ForeignKey(
        SupplierCategoryProduct,
        verbose_name="Категория каталога поставщика",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    group_supplier = models.ForeignKey(
        SupplierGroupProduct,
        verbose_name="Группа каталога поставщика",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    category_supplier_all = models.ForeignKey(
        "SupplierCategoryProductAll",
        verbose_name="Приходящая категории товара от поставщиков",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    percent = models.FloatField(
        "Процент скидки",
        blank=True,
        null=True,
    )

    is_tag_pre_sale = models.BooleanField(
        "Скидка действует по предоплате", default=False
    )

    class Meta:
        verbose_name = "Скидка"
        verbose_name_plural = "Скидки"

    def __str__(self):
        # вывод примененной категории в название скидки в админку
        name = ""
        if self.category_supplier_all:
            name = self.category_supplier_all.name
        elif self.group_supplier:
            name = self.group_supplier.name
        elif self.category_supplier:
            name = self.category_supplier.name
        elif self.vendor:
            name = self.vendor.name
        return f"Скидка {self.supplier}|{name}:{self.percent}%"

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)
        from apps.product.models import Price

        # обновление цен товаров связанной группы
        if self.category_supplier_all:
            price = Price.objects.filter(
                prod__category_supplier_all=self.category_supplier_all
            )
        elif self.group_supplier:
            price = Price.objects.filter(prod__group_supplier=self.group_supplier)
        elif self.category_supplier:
            price = Price.objects.filter(prod__category_supplier=self.category_supplier)
        elif self.vendor:
            price = Price.objects.filter(prod__vendor=self.vendor)
        elif self.supplier:
            price = Price.objects.filter(prod__supplier=self.supplier)

        if self.is_tag_pre_sale == False:

            def background_task():
                # Долгосрочная фоновая задача
                for price_one in price:
                    print(price_one)
                    price_one._change_reason = "Автоматическое"
                    price_one.save()
                    

            daemon_thread = threading.Thread(target=background_task)
            daemon_thread.setDaemon(True)
            daemon_thread.start()
