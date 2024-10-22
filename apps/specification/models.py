import datetime
from django.db import models
from django.urls import reverse


from apps.core.models import Currency
from apps.product.models import Price, Product
from apps.specification.utils import get_document_path
from simple_history.models import HistoricalRecords
from apps.user.models import AdminUser
import uuid
# Create your models here.


class Specification(models.Model):

    id_bitrix = models.PositiveIntegerField(
        "Номер сделки битрикс",
        null=True,
    )
    number = models.CharField(
        "Номер спецификации",
        default=uuid.uuid4,
        max_length=1000,
        null=True,

    )
    date = models.DateField(default=datetime.date.today, verbose_name="Дата добавления")
    date_update = models.DateField(auto_now=True, verbose_name="Дата обновления")
    date_stop = models.DateField(verbose_name="Дата окончания")
    tag_stop = models.BooleanField("Действительно", default=True)
    total_amount = models.FloatField("Сумма спецификации", null=True, default=None)
    admin_creator = models.ForeignKey(
        AdminUser,
        on_delete=models.PROTECT,
        verbose_name="Администратор",
        null=True,
        default=None,
    )
    file = models.FileField(
        "Фаил", upload_to=get_document_path, null=True, default=None
    )
    is_prepay = models.BooleanField("Предоплата", default=False)
    cart = models.OneToOneField(
        "product.Cart",
        on_delete=models.PROTECT,
        verbose_name="Корзина",
        null=True,
    )
    comment = models.CharField(
        "Комментарий",
        default=None,
        max_length=1000,
        blank=True,
        null=True,
    )
    date_delivery = models.CharField(
        "Дата поставки",
        default=None,
        max_length=1000,
        blank=True,
        null=True,
    )
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    class Meta:
        verbose_name = "Спецификация"
        verbose_name_plural = "Спецификации"

    def __str__(self):
        return f"{self.id_bitrix}"

    def save(self, *args, **kwargs):
        # from apps.core.utils import create_time_stop_specification

        # data_stop = create_time_stop_specification()
        # self.date_stop = data_stop
        # self.tag_stop = True

        super().save(*args, **kwargs)

    def get_order_bill(self):
        from apps.client.models import Order

        try:

            order = Order.objects.get(specification=self)

            return order.bill_file
        except Order.DoesNotExist:
            return None
        
    def get_absolute_url(self):

            return reverse(
                "admin_specification:one_specifications",
                kwargs={
                    "pk": self.pk,
                },
            )   
            
    def get_history_url(self):

        return reverse(
            "admin_specification:history_admin",
            kwargs={
                "pk": self.pk,
            },
        )           


class ProductSpecification(models.Model):
    specification = models.ForeignKey(
        Specification,
        on_delete=models.CASCADE,
        verbose_name="Товар",
        blank=True,
        null=True,
    )
    product = models.ForeignKey(
        Product,
        verbose_name="Продукты",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    # product_in_cart = models.ForeignKey(
    #     "product.ProductCart",
    #     verbose_name="Продукт в корзине",
    #     on_delete=models.PROTECT,
    #     blank=True,
    #     null=True,
    # )

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

    product_currency = models.ForeignKey(
        Currency,
        verbose_name="Валюта",
        on_delete=models.PROTECT,
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


    quantity = models.IntegerField(
        "количество товара",
        blank=True,
        null=True,
    )

    price_one = models.FloatField("Цена одного на момент формирования")
    price_all = models.FloatField(
        "Цена всего товара на момент формирования",
        blank=True,
        null=True,
    )
    price_one_motrum = models.FloatField(
        "Цена мотрум  в рублях",
        blank=True,
        null=True,
    )
    price_all_motrum = models.FloatField(
        "Цена Motrum в рублях",
        blank=True,
        null=True,
    )
    price_exclusive = models.BooleanField("Цена по запросу", default=False)
    extra_discount = models.FloatField(
        "Процент дополнительной скидки",
        blank=True,
        null=True,
    )
    date_delivery = models.DateField(verbose_name="Дата поставки товара", null=True)
    text_delivery = models.CharField(
        "Дата поставки товара текстом для счета",
        default=None,
        max_length=1000,
        blank=True,
        null=True,
    )
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    class Meta:
        verbose_name = "Спецификация продукт"
        verbose_name_plural = "Спецификации Продукты"

    def __str__(self):
        if self.product:
            return f"{self.product}"
        else:
            return f"{self.product_new}"

    # def save(self, *args, **kwargs):
    #     # если с админки сохранение(работало правильно до отделения сборки спецификаций на фронте)
    #     # if self.price_all == None:
    #     #     spec = Specification.objects.get(id=self.specification.id)
    #     #     price = Price.objects.get(prod=self.product)
    #     #     if self.price_one != price.price_supplier:
    #     #         self.price_exclusive = True
    #     #     price_current = price.currency.words_code
    #     #     self.product_currency = price.currency
    #     #     self.price_all = self.price_one * self.quantity

    #     #     # отметка о валютности + добавление общец суммы
    #     #     if price_current != "RUB":
    #     #         # spec.tag_currency = price.currency
    #     #         spec.currency_product = True
    #     #     print(spec.total_amount)
    #     #     if spec.total_amount is None:
    #     #         total_init = 0
    #     #     else:
    #     #         total_init = spec.total_amount

    #     #     total = total_init + self.price_all
    #     #     spec.total_amount = total
    #     #     spec.save()

    #     super().save(*args, **kwargs)


# @receiver(post_save)
# def my_callback(sender, instance, *args, **kwargs):
#     sums = ProductSpecification.objects.filter(specification=instance.id).aggregate(Sum("price_all"))
#     spes = Specification.objects.get(id = instance.id)
#     spes.total_amount = sums['price_all__sum']
#     spes.save()
#     print(sender)
#     print(instance.id)
