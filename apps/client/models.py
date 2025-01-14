import datetime
from pyexpat import model
from sys import version
from token import TYPE_COMMENT
from django.db import models
from django.db.models import Case, Value, When
from django.urls import reverse
from simple_history.models import HistoricalRecords

# Create your models here.


from apps.core.models import BaseInfo, BaseInfoAccountRequisites, TypeDelivery
from apps.specification.models import Specification
from apps.specification.utils import get_document_bill_path, get_shipment_doc_path
from apps.supplier.models import Discount
from apps.user.models import AdminUser, CustomUser


# клиент на сайте
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

    # добавление менеджера клиенту рандом
    def add_manager(self):
        if self.manager == None:
            old_user = Client.objects.filter().last()
            old_user_manager = old_user.manager

            # не такой как у последнего клиента
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
TYPE_CLIENT = (
    ("1", "Юридическое лицо"),
    ("2", "ИП"),
)
#   {
#             "ID": "1",
#             "NAME": "Организация"
#         },
#         {
#             "ID": "2",
#             "NAME": "ИП"
#         },
#         {
#             "ID": "3",
#             "NAME": "Физ. лицо"
#         },
#         {
#             "ID": "4",
#             "NAME": "Организация (доп.)"
#         }


# TODO: unique=True вернуть
# юрлицо  клиента главна сущность ИНН
class Requisites(models.Model):
    client = models.ForeignKey(
        Client,
        verbose_name="Клиент",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    id_bitrix = models.PositiveIntegerField(
        "Номер клиента битрикс",
        null=True,
        blank=True,
    )
    number_spec = models.PositiveIntegerField(
        "Номер спецификации клиента", null=True, blank=True, default=0
    )

    contract = models.CharField(
        "Договор",
        max_length=50,
        blank=True,
        null=True,
    )
    contract_date = models.DateField(
        "Договор дата",
        blank=True,
        null=True,
    )
    discount = models.FloatField(
        "Процент скидки",
        blank=True,
        null=True,
    )
    type_payment = models.CharField(
        "Тип оплаты", max_length=100, choices=TYPE_PAYMENT, default="100% prepay"
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

    # type_delivery = models.CharField(
    #     "Тип доставки",
    #     max_length=1000,
    #     blank=True,
    #     null=True,
    # )

    legal_entity = models.CharField(
        "Юридическое лицо",
        max_length=150,
    )
    # ,unique=True
    inn = models.CharField(
        "ИНН",
        max_length=12,
        # unique=True
    )
    type_client = models.CharField(
        "Тип клиента", max_length=100, choices=TYPE_CLIENT, default="1"
    )

    # kpp = models.CharField(
    #     "КПП",
    #     max_length=10,
    # )
    # ogrn = models.CharField(
    #     "ОГРН",
    #     max_length=15,
    #     blank=True,
    #     null=True,
    # )
    # legal_post_code = models.PositiveIntegerField(
    #     "Юридический адрес :индекс",
    # )
    # legal_city = models.CharField(
    #     "Юридический адрес : город",
    #     max_length=50,
    # )
    # legal_address = models.CharField(
    #     "Юридический адрес : адрес",
    #     max_length=200,
    # )
    # postal_post_code = models.CharField(
    #     "Почтовый адрес :индекс",
    #     max_length=10,
    # )
    # postal_city = models.CharField(
    #     "Почтовый адрес : город",
    #     max_length=50,
    # )
    # postal_address = models.CharField(
    #     "Почтовый адрес : адрес",
    #     max_length=200,
    # )
    # tel = models.CharField(
    #     "Телефон",
    #     max_length=200,
    #     blank=True,
    #     null=True,
    # )

    class Meta:
        verbose_name = "Юридическое лицо"
        verbose_name_plural = "Юридические лица"

    def __str__(self):
        return self.legal_entity

    # получить название типа оплаты в шаблон
    def get_type_payment(self):
        for choice in TYPE_PAYMENT:
            if choice[0] == self.type_payment:
                return choice[1]
        return ""


# реквизиты компании прикрепленные к кпп
class RequisitesOtherKpp(models.Model):
    requisites = models.ForeignKey(
        Requisites, verbose_name="Реквизиты", on_delete=models.CASCADE
    )
    kpp = models.CharField(
        "КПП",
        max_length=10,
        blank=True,
        null=True,
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

    def __str__(self):
        return f"{self.requisites.legal_entity} {self.kpp}"


# типы адресов битрикс
TYPE_ADDRESS = (
    (1, "Фактический адрес"),
    (4, "Адрес регистрации"),
    (6, "Юридический адрес"),
    (9, "Адрес бенефициара"),
)


# адреса реквизитов кпп
class RequisitesAddress(models.Model):
    requisitesKpp = models.ForeignKey(
        RequisitesOtherKpp, verbose_name="Реквизиты", on_delete=models.CASCADE
    )
    type_address_bx = models.CharField(max_length=100, choices=TYPE_ADDRESS, default=4)
    country = models.CharField(
        "Страна",
        max_length=100,
        null=True,
        blank=True,
    )
    post_code = models.PositiveIntegerField(
        "Индекс",
        null=True,
        blank=True,
    )
    region = models.CharField(
        "Регион",
        max_length=150,
        null=True,
        blank=True,
    )
    province = models.CharField(
        "Область",
        max_length=150,
        null=True,
        blank=True,
    )
    city = models.CharField(
        "Город",
        max_length=150,
        null=True,
        blank=True,
    )
    address1 = models.CharField(
        "Адрес",
        max_length=200,
        null=True,
        blank=True,
    )
    address2 = models.CharField(
        "Дом",
        max_length=200,
        null=True,
        blank=True,
    )


# банковские реквизиты прикрепленны к рекам с кпп
class AccountRequisites(models.Model):
    requisitesKpp = models.ForeignKey(
        RequisitesOtherKpp, verbose_name="Реквизиты", on_delete=models.CASCADE
    )
    # requisites = models.ForeignKey(
    #     Requisites, verbose_name="Реквизиты", on_delete=models.CASCADE
    # )
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


# хранение номеров телефон всех кто осатвил контактные данные на сайте
class EmailsAllWeb(models.Model):
    name = models.CharField("Контактное лицо", max_length=40, blank=True, null=True)
    phone = models.CharField(
        "Номер телефона",
        max_length=40,
    )


# контакты оставленные для связаться
class EmailsCallBack(models.Model):
    name = models.CharField("Контактное лицо", max_length=40, blank=True, null=True)
    phone = models.CharField(
        "Номер телефона",
        max_length=40,
    )


# статусы которые в окт и на сайте- конвертация из статусов битрикс
STATUS_ORDER = (
    ("", "----"),
    ("PROCESSING", "В обработке"),
    ("PAYMENT", "Счёт на оплату"),
    ("IN_MOTRUM", "Заказ у поставщика"),
    ("SHIPMENT_AUTO", "На доставке "),
    ("SHIPMENT_PICKUP", "Готов к отгрузке самовывозом"),
    ("CANCELED", "Отменен"),
    ("COMPLETED", "Заказ завершен"),
)
# статусы которые есть в битрикс
STATUS_ORDER_BITRIX = (
    ("PROCESSING", "NEW"),
    ("PROCESSING", "PREPARATION"),
    ("PROCESSING", "C8:NEW"),
    ("PROCESSING", "C8:PREPARATION"),
    ("PROCESSING", "C8:PREPAYMENT_INVOICE"),  # На удаление
    ("PAYMENT", "C8:EXECUTING"),
    ("IN_MOTRUM", "C8:FINAL_INVOICE"),
    ("SHIPMENT_", "C8:1"),
    ("CANCELED", "C8:LOSE"),
    ("CANCELED", "C8:2"),
    ("COMPLETED", "C8:WON"),
)
CLEAN_STATUS_ORDER_BITRIX = (
    ("NEW", "Квалификация"),
    ("PREPARATION", "Квалификация"),
    ("C8:NEW", "Не обработано"),
    ("C8:PREPARATION", "Подготовка расчета (счета)"),
    ("C8:PREPAYMENT_INVOICE", "КП отправлено"),  # На удаление
    ("C8:EXECUTING", "Счёт отправлен"),
    ("C8:FINAL_INVOICE", "Поставка оборудования в Мотрум"),
    ("C8:1", "Отгрузка оборудования заказчику"),
    ("C8:LOSE", "Отложенные"),
    ("C8:2", "Провальные"),
    ("C8:WON", "Сделка успешна"),
)
# STATUS_ORDER_INT = (
#     (1, "PROCESSING"),
#     (2, "PAYMENT"),
#     (3, "IN_MOTRUM"),
#     (4, "SHIPMENT_AUTO"),
#     (5, "SHIPMENT_PICKUP"),
#     (6, "CANCELED"),
#     (7, "COMPLETED"),
# )


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
    text_name = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )
    id_bitrix = models.PositiveIntegerField(
        "Номер сделки битрикс",
        null=True,
    )
    manager = models.ForeignKey(
        AdminUser, blank=True, null=True, on_delete=models.CASCADE
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
    comment = models.CharField(
        "Комментарий",
        default=None,
        max_length=1000,
        blank=True,
        null=True,
    )

    type_delivery = models.ForeignKey(
        TypeDelivery,
        verbose_name="Тип доставки ",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    motrum_requisites = models.ForeignKey(
        BaseInfoAccountRequisites,
        verbose_name="Реквизиты мотрум ",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    bill_name = models.PositiveIntegerField(
        "Номер счета",
        default=None,
        null=True,
    )
    bill_file = models.FileField(
        "Фаил счета",
        upload_to=get_document_bill_path,
        blank=True,
        null=True,
    )
    bill_file_no_signature = models.FileField(
        "Фаил счета без печатей",
        upload_to=get_document_bill_path,
        blank=True,
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
    bill_tag_stop = models.BooleanField("Действительно", default=True)
    bill_id_bx = models.PositiveIntegerField(
        "Номер id счета bitrix",
        default=None,
        null=True,
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

    # создание документов счета
    def create_bill(
        self,
        request,
        is_contract,
        order,
        # bill_name,
        post_update,
        type_save,
    ):

        from apps.core.utils import create_time_stop_specification
        from apps.client.utils import crete_pdf_bill
        from apps.notifications.models import Notification

        pdf_file, pdf_name, file_path_no_sign, version = crete_pdf_bill(
            self.specification.id,
            request,
            is_contract,
            order,
            # bill_name,
            self.type_delivery,
            post_update,
            type_save,
        )
        if pdf_file:
            # if post_update:
            #     bill_date_start = self.bill_date_start
            #     data_stop = self.bill_date_stop
            # else:
            #     self.bill_date_start = datetime.date.today()
            #     bill_date_start = datetime.date.today()
            #     data_stop = create_time_stop_specification()
            #     self.bill_date_stop = data_stop
            #     self.status = "PAYMENT"
            self.bill_date_start = datetime.date.today()
            bill_date_start = datetime.date.today()
            data_stop = create_time_stop_specification()
            self.bill_date_stop = data_stop

            # if type_save == "new":
            #     self.status = "PAYMENT"
            # elif type_save == "update":
            #     pass
            # elif type_save == "hard_update":
            #     self.status = "PAYMENT"

            self.bill_file = pdf_file
            self.bill_file_no_signature = file_path_no_sign
            self.bill_sum = self.specification.total_amount
            self.bill_name = pdf_name

            if self.client:
                Notification.add_notification(self.id, "DOCUMENT_BILL")
            self._change_reason = "Ручное"
            self.save()

            old_document = OrderDocumentBill.objects.filter(order=self)
            if old_document:
                old_document.update(is_active=False)

            OrderDocumentBill.objects.create(
                order=self,
                bill_name=pdf_name,
                bill_file=pdf_file,
                bill_date_start=bill_date_start,
                bill_date_stop=data_stop,
                bill_file_no_signature=None,
                bill_sum=self.bill_sum,
                version=version,
            )
            OrderDocumentBill.objects.create(
                order=self,
                bill_name=pdf_name,
                bill_file=None,
                bill_file_no_signature=file_path_no_sign,
                bill_date_start=bill_date_start,
                bill_date_stop=data_stop,
                bill_sum=self.bill_sum,
                version=version,
            )
            return self.id
        else:
            return None

    # Получение руского названия статуса в шаблоны
    def get_status_name(self):
        for choice in STATUS_ORDER:
            if choice[0] == self.status:
                return choice[1]
        return ""


# фаилы счетов все версии
class OrderDocumentBill(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    is_active = models.BooleanField("Активно", default=True)
    bill_name = models.PositiveIntegerField(
        "Номер счета",
        default=None,
        null=True,
    )
    bill_file = models.FileField(
        "Фаил счета",
        default=None,
        null=True,
    )
    bill_file_no_signature = models.FileField(
        "Фаил счета без печатей",
        default=None,
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
    version = models.PositiveIntegerField(
        "Версия в одну дату",
        default=None,
        null=True,
    )


class PaymentTransaction(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    date = models.DateField(
        verbose_name="Дата оплаты",
        blank=True,
        null=True,
    )
    amount = models.FloatField(
        "Сумма счета",
        blank=True,
        null=True,
    )
    # history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))


class DocumentShipment(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    date = models.DateField(
        verbose_name="Дата оплаты",
        blank=True,
        null=True,
    )
    file = models.FileField(
        "Фаил счета",
        upload_to=get_shipment_doc_path,
        blank=True,
        null=True,
    )
    # history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))
