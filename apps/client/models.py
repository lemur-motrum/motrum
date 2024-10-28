import datetime
from pyexpat import model
from token import TYPE_COMMENT
from django.db import models
from django.db.models import Case, Value, When
from django.urls import reverse
from simple_history.models import HistoricalRecords
# Create your models here.


from apps.core.models import BaseInfoAccountRequisites
from apps.specification.models import Specification
from apps.specification.utils import get_document_bill_path
from apps.supplier.models import Discount
from apps.user.models import AdminUser, CustomUser


class Client(CustomUser):
    user = models.OneToOneField(CustomUser, parent_link=True, on_delete=models.CASCADE)
    contact_name = models.CharField(
        "Контактное лицо", max_length=40, blank=True, null=True
    )
    phone = models.CharField("Номер телефона", max_length=40, unique=True)
    manager = models.ForeignKey(
        AdminUser, blank=True, null=True, on_delete=models.CASCADE
    )
    percent = models.FloatField(
        "Процент скидки",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def save(self, *args, **kwargs):
        # self.password = "1234"
        # self.set_password(self.password)
        self.username = self.phone

        super().save(*args, **kwargs)

    def __str__(self):
        return self.phone

    def add_manager(self):
        if self.manager == None:
            old_user = Client.objects.filter().last()

            old_user_manager = old_user.manager
            if old_user_manager:
                admin = (
                    AdminUser.objects.filter(admin_type="BASE")
                    .exclude(id=old_user_manager.id)
                    .order_by("?")
                    .first()
                )
                self.manager = admin
                self.save()

            else:
                admin = (
                    AdminUser.objects.filter(admin_type="BASE").order_by("?").first()
                )
                self.manager = admin
                self.save()

    # def send_email_notification(self,text_email):
TYPE_PAYMENT = (
    ("100% prepay", "100% предоплата"),
    ("payment in installments", "Оплата частями"),
    ("100% postpay", "100% постоплата"),
)

class Requisites(models.Model):
    client = models.ForeignKey(Client, verbose_name="Клиент", on_delete=models.CASCADE,null=True,blank=True,)
    
    contract = models.CharField(
        "Договор",
        max_length=50,
        blank=True,
        null=True,
    )
    discount = models.FloatField(
        "Процент скидки",
        blank=True,
        null=True,
    )
    type_payment = models.CharField(
        "Тип оплаты",
        max_length=100,
        choices=TYPE_PAYMENT,
        default="100% prepay"

    )
    prepay_persent = models.FloatField(
        "Процент предоплаты",
        default="100",
        blank=True,
        null=True,
    )
    
    postpay_persent = models.FloatField(
        "Процент постоплаты",
        default="0",
        blank=True,
        null=True,
    )
    
    type_delivery = models.CharField(
        "Тип доставки",
        max_length=1000,
        blank=True,
        null=True,
    )
    
    legal_entity = models.CharField(
        "Юридическое лицо",
        max_length=150,
    )
    # ,unique=True
    inn = models.CharField(
        "ИНН",
        max_length=12,
    )
    kpp = models.CharField(
        "КПП",
        max_length=10,
    )
    ogrn = models.CharField(
        "ОГРН",
        max_length=15,
        blank=True,
        null=True,
    )
    legal_post_code = models.PositiveIntegerField(
        "Юридический адрес :индекс",
    )
    legal_city = models.CharField(
        "Юридический адрес : город",
        max_length=50,
    )
    legal_address = models.CharField(
        "Юридический адрес : адрес",
        max_length=200,
    )
    postal_post_code = models.CharField(
        "Почтовый адрес :индекс",
        max_length=10,
    )
    postal_city = models.CharField(
        "Почтовый адрес : город",
        max_length=50,
    )
    postal_address = models.CharField(
        "Почтовый адрес : адрес",
        max_length=200,
    )
    tel = models.CharField(
        "Телефон",
        max_length=200,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Реквизиты"
        verbose_name_plural = "Реквизиты"

    def __str__(self):
        return self.legal_entity
    
    
    def get_type_payment(self):
        for choice in TYPE_PAYMENT:
            if choice[0] == self.type_payment:
                return choice[1]
        return ""


class AccountRequisites(models.Model):
    requisites = models.ForeignKey(
        Requisites, verbose_name="Реквизиты", on_delete=models.CASCADE
    )
    account_requisites = models.CharField(
        "Расчётный счёт",
        max_length=30,
    )
    bank = models.CharField(
        "Банк",
        max_length=200,
    )
    kpp = models.CharField(
        "Корреспондентский счет (к/с)",
        max_length=20,
    )
    bic = models.CharField(
        "БИК",
        max_length=10,
    )

    class Meta:
        verbose_name = "Расчётный счёт"
        verbose_name_plural = "Расчётные счёта"

    def __str__(self):
        return self.account_requisites


class EmailsCallBack(models.Model):
    name = models.CharField("Контактное лицо", max_length=40, blank=True, null=True)
    phone = models.CharField(
        "Номер телефона",
        max_length=40,
    )


# class ClientDiscount(models.Model):
#     requisites = models.OneToOneField(Requisites,verbose_name="Юр.лицо", on_delete=models.CASCADE)
#     percent = models.FloatField(
#             "Процент скидки",
#         )

#     class Meta:
#         verbose_name = "Скидка юрлица"
#         verbose_name_plural = "Скидки юрлиц"

#     def __str__(self):
#         return self.name
# PROCESSING = 1
# PAYMENT = 2
# IN_MOTRUM = 3
# SHIPMENT_AUTO = 4
# SHIPMENT_PICKUP = 5
# CANCELED = 6
# COMPLETED = 7

STATUS_ORDER = (
    ('', '----'),
    ("PROCESSING", "В обработке"),
    ("PAYMENT", "Счёт на оплату"),
    ("IN_MOTRUM", "Заказ у поставщика"),
    ("SHIPMENT_AUTO", "На доставке "),
    ("SHIPMENT_PICKUP", "Готов к отгрузке самовывозом"),
    ("CANCELED", "Отменен"),
    ("COMPLETED", "Заказ завершен"),
)
STATUS_ORDER_INT = (
    (1, "PROCESSING"),
    (2, "PAYMENT"),
    (3, "IN_MOTRUM"),
    (4, "SHIPMENT_AUTO"),
    (5, "SHIPMENT_PICKUP"),
    (6, "CANCELED"),
    (7, "COMPLETED"),
)

import random

class Order(models.Model):
    client = models.ForeignKey(
        Client,
        verbose_name="Клиент",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    name = models.PositiveIntegerField(
        "номер заказа",
    )
    id_bitrix = models.PositiveIntegerField(
        "Номер сделки битрикс",
        null=True,
    )
    date_order = models.DateField(
        default=datetime.date.today,
        verbose_name="Дата создания заказа",
        blank=True,
        null=True,
    )
    date_completed = models.DateField(
        verbose_name="Дата завершения",
        blank=True,
        null=True,
    )
    date_update = models.DateField(auto_now=True, verbose_name="Дата обновления")

    status = models.CharField(
        max_length=100, choices=STATUS_ORDER, default="PROCESSING"
    )
    specification = models.OneToOneField(
        Specification,
        verbose_name="Спецификация",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    cart = models.OneToOneField(
        "product.Cart",
        verbose_name="Корзина",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    requisites = models.ForeignKey(
        Requisites,
        verbose_name="Реквизиты заказа",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    account_requisites = models.ForeignKey(
        AccountRequisites,
        verbose_name="Расчетный счет",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    prepay_persent = models.FloatField(
        "Процент предоплаты",
        blank=True,
        null=True,
    )
    
    postpay_persent = models.FloatField(
        "Процент постоплаты",
        blank=True,
        null=True,
    )
    
    motrum_requisites = models.ForeignKey(
        BaseInfoAccountRequisites,
        verbose_name="Реквизиты мотрум для сделки",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    bill_name = models.CharField(
        max_length=1000,  default=random.randint(0, 9999),blank=True,
        null=True,
    )
    bill_file = models.FileField(
        "Фаил счета", upload_to=get_document_bill_path, blank=True,
        null=True,
    )
    bill_date_start = models.DateField(
        verbose_name="Дата создания счета",
        blank=True,
        null=True,
    )
    bill_date_stop = models.DateField(
        verbose_name="Дата окончания счета",
        blank=True,
        null=True,
    )
    bill_sum = models.FloatField(
        "Сумма счета",
        blank=True,
        null=True,
    )
    bill_sum_paid = models.FloatField(
        "Оплаченная сумма", blank=True, null=True, default=0
    )

    act_file = models.FileField(
        "Фаил акта поставки", upload_to=get_document_bill_path, null=True, default=None
    )
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return str(self.id)

    def create_bill(self, request, is_contract,order):
        from apps.core.utils import create_time_stop_specification
        from apps.client.utils import crete_pdf_bill
        from apps.notifications.models import Notification
        print(is_contract,order)
        self.bill_date_start = datetime.date.today()
        print(is_contract,order)
        data_stop = create_time_stop_specification()
        print(data_stop)
        self.bill_date_stop = data_stop

        pdf = crete_pdf_bill(self.specification.id,request,is_contract,order,)
        if pdf:
            self.bill_file = pdf
            self.bill_sum = self.specification.total_amount
            self.bill_name = self.specification.id
            self.status = "PAYMENT"
            if self.client:
                Notification.add_notification(self.id, "DOCUMENT_BILL")
            self._change_reason = "Ручное"
            self.save()
            
            return self.id
        else:
            return None

    def get_status_name(self):
        for choice in STATUS_ORDER:
            if choice[0] == self.status:
                return choice[1]
        return ""
    



# class Document(models.Model):
#     client = models.ForeignKey(
#         Client,
#         verbose_name="Клиент",
#         on_delete=models.PROTECT,
#         blank=True,
#         null=True,
#     )
#     order = models.ForeignKey(
#         Order,
#         verbose_name="Заказ",
#         on_delete=models.PROTECT,
#         blank=True,
#         null=True,
#     )
#     date = models.DateField(default=datetime.date.today, verbose_name="Дата добавления")
