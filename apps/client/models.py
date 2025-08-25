import datetime
from pyexpat import model
from sys import version
from token import TYPE_COMMENT
from django.db import models
from django.db.models import Case, Value, When
from django.dispatch import receiver
from django.urls import reverse
from simple_history.models import HistoricalRecords
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save
from django.template import loader

# Create your models here.


from apps.core.models import BaseInfo, BaseInfoAccountRequisites, TypeDelivery

from apps.core.utils_web import send_email_message_and_file_alternative
from apps.logs.utils import error_alert
from apps.product.models import CategoryProduct
from apps.specification.models import Specification
from apps.specification.utils import get_document_bill_path, get_shipment_doc_path
from apps.supplier.models import Discount
from apps.user.models import AdminUser, CustomUser
from middlewares.middlewares import RequestMiddleware
from project.settings import BASE_DIR, BASE_MANAGER_FOR_BX, DOMIAN, IS_TESTING


# клиент на сайте
class Client(CustomUser):
    user = models.OneToOneField(CustomUser, parent_link=True, on_delete=models.PROTECT)
    contact_name = models.CharField(
        "Контактное лицо", max_length=40, blank=True, null=True
    )
    middle_name = models.CharField("Отчество", max_length=50, null=True, blank=True)
    phone = models.CharField("Номер телефона", max_length=40, unique=True)
    manager = models.ForeignKey(
        AdminUser, blank=True, null=True, on_delete=models.PROTECT
    )
    percent = models.FloatField(
        "Процент скидки",
        blank=True,
        null=True,
    )
    position = models.CharField("Номер телефона", max_length=200, null=True, blank=True)
    bitrix_id_client = models.PositiveIntegerField(
        "Номер  битрикс",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Клиент сайта"
        verbose_name_plural = "Клиенты на сайте"

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
            base_manager = AdminUser.objects.get(email=BASE_MANAGER_FOR_BX)
            print(base_manager)
            self.manager = base_manager
            self.save()

    def add_manager_random(self):
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


class PhoneClient(models.Model):
    phone = models.CharField("Номер телефона", max_length=40)
    client = models.ForeignKey(
        Client,
        verbose_name="Клиент",
        on_delete=models.CASCADE,
    )


TYPE_PAYMENT = (
    ("100% prepay", "100% предоплата"),
    ("payment in installments", "Оплата частями"),
    ("100% postpay", "100% постоплата"),
)
# TYPE_CLIENT = (
#     ("1", "Юридическое лицо"),
#     ("2", "ИП"),
#     ("3", "Физ. лицо"),
#     ("4", "Организация (доп.)"),
# )
TYPE_CLIENT = (
    ("1", "Юридическое лицо"),
    ("3", "ИП"),
    ("5", "Физ. лицо"),
)


# TODO: unique=True вернуть
# юрлицо  клиента главна сущность ИНН
class Requisites(models.Model):
    client = models.ForeignKey(
        Client,
        verbose_name="Клиент",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )  # НА УДАЛЕНИЕ

    id_bitrix = models.CharField(
        "Id реквизита в битрикс",
        max_length=1000,
        blank=True,
        null=True,
    )

    number_spec = models.PositiveIntegerField(
        "Номер спецификации клиента", null=True, blank=True, default=0
    )

    contract = models.CharField(
        "Договор",
        max_length=200,
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
    postpay_persent_text = models.CharField(
        "Процент постоплаты текст",
        default="в течение 5 дней с момента отгрузки со склада Поставщика.",
        max_length=200,
        blank=True,
        null=True,
    )
    
    postpay_persent_2 = models.FloatField(
        "Процент постоплаты 2",
        default=None,
        blank=True,
        null=True,
    )
    postpay_persent_text_2 = models.CharField(
        "Процент предоплаты текст 2",
        default=None,
        max_length=200,
        blank=True,
        null=True,
    )
    postpay_persent_3 = models.FloatField(
        "Процент постоплаты 3",
        default=None,
        blank=True,
        null=True,
    )
    postpay_persent_text_3 = models.CharField(
        "Процент предоплаты текст 3",
        default=None,
        max_length=200,
        blank=True,
        null=True,
    )
    manager = models.ForeignKey(
        AdminUser,
        verbose_name="Менеджер в битрикс",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

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
    first_name = models.CharField(
        "Имя ИП",
        max_length=150,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        "Фамилия ИП",
        max_length=150,
        blank=True,
        null=True,
    )
    middle_name = models.CharField(
        "Отчество ИП",
        max_length=150,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Юридическое лицо"
        verbose_name_plural = "Юридические лица"

    def __str__(self):
        return self.legal_entity

    def save(self, *args, **kwargs):
        print(self)
        print("save req")
        super().save(*args, **kwargs)

    # получить название типа оплаты в шаблон
    def get_type_payment(self):
        for choice in TYPE_PAYMENT:
            if choice[0] == self.type_payment:
                return choice[1]
        return ""

    # получить название типа rkbtynf
    def get_type_client(self):
        print("TYPE_CLIENT")
        for choice in TYPE_CLIENT:
            if choice[0] == self.type_client:
                return choice[1]
        return ""


# реквизиты компании прикрепленные к кпп
class RequisitesOtherKpp(models.Model):
    id_bitrix = models.PositiveIntegerField(
        "Номер клиента битрикс",
        null=True,
        blank=True,
    )
    requisites = models.ForeignKey(
        Requisites, verbose_name="Реквизиты", on_delete=models.PROTECT
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
        max_length=1000,
    )
    legal_address = models.CharField(
        "Юридический адрес : адрес",
        max_length=1000,
    )
    postal_post_code = models.CharField(
        "Почтовый адрес :индекс",
        max_length=150,
    )
    postal_city = models.CharField(
        "Почтовый адрес : город",
        max_length=1000,
    )
    postal_address = models.CharField(
        "Почтовый адрес : адрес",
        max_length=1000,
    )
    tel = models.CharField(
        "Телефон",
        max_length=200,
        blank=True,
        null=True,
    )
    email = models.CharField(
        "Email",
        max_length=200,
        null=True,
        blank=True,
    )
   
    class Meta:
        verbose_name = "Реквизиты и данные"
        verbose_name_plural = "Реквизиты и данные"
    def __str__(self):
        return f"{self.requisites.legal_entity} {self.kpp}"


# типы адресов битрикс
TYPE_ADDRESS = (
    (1, "Фактический адрес"),
    (4, "Адрес регистрации"),
    (6, "Юридический адрес"),
    (8, "Адрес для корреспонденции"),
    (9, "Адрес бенефициара"),
    (11, "Адрес доставки"),
    ("web-lk-adress", "Юридический адрес сайт"),
)


class ClientRequisites(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
    )
    requisitesotherkpp = models.ForeignKey(
        RequisitesOtherKpp,
        verbose_name="",
        on_delete=models.CASCADE,
    )


# адреса реквизитов кпп
class RequisitesAddress(models.Model):
    requisitesKpp = models.ForeignKey(
        RequisitesOtherKpp, verbose_name="Реквизиты", on_delete=models.PROTECT
    )
    type_address_bx = models.CharField(max_length=100, choices=TYPE_ADDRESS, default=6)
    country = models.CharField(
        "Страна",
        max_length=500,
        null=True,
        blank=True,
    )
    post_code = models.PositiveIntegerField(
        "Индекс",
        null=True,
        blank=True,
    )
    region = models.CharField(
        "Область",
        max_length=150,
        null=True,
        blank=True,
    )
    province = models.CharField(
        "район",
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
        RequisitesOtherKpp, verbose_name="Реквизиты", on_delete=models.PROTECT
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


# статусы которые в окт и на сайте
STATUS_ORDER = (
    ("", "----"),
    ("PRE-PROCESSING", "В обработке"),
    ("PROCESSING", "В обработке"),
    ("PAYMENT", "Счёт на оплату"),
    ("IN_MOTRUM", "Заказ у поставщика"),
    ("SHIPMENT_AUTO", "На доставке"),
    ("SHIPMENT_PICKUP", "Готов к отгрузке самовывозом"),
    ("CANCELED", "Отменен"),
    ("COMPLETED", "Заказ завершен"),
)
# конвертация статусов битрикс в статусы окт
STATUS_ORDER_BITRIX = (
    ("PRE-PROCESSING", "NEW"),
    ("PRE-PROCESSING", "PREPARATION"),
    ("PRE-PROCESSING", "C8:NEW"),
    ("PROCESSING", "C8:PREPARATION"),
    ("PROCESSING", "C8:PREPAYMENT_INVOICE"),  # На удаление
    ("PAYMENT", "C8:EXECUTING"),
    ("IN_MOTRUM", "C8:FINAL_INVOICE"),
    ("SHIPMENT_", "C8:1"),
    ("CANCELED", "C8:LOSE"),
    ("CANCELED", "C8:2"),
    ("COMPLETED", "C8:WON"),
)
# чистые статусы битрикс
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
TYPE_ORDER_NAME = (
    ("ИМ", "ИМ"),
    ("ОКТ", "ОКТ"),
    
)

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
        blank=True,
        null=True,
    )
    text_name = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )
    id_bitrix = models.PositiveIntegerField(
        "Номер сделки битрикс",
        null=True,
        # unique=True
    )
    manager = models.ForeignKey(
        AdminUser, blank=True, null=True, on_delete=models.PROTECT
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
        max_length=100, choices=STATUS_ORDER, default="PRE-PROCESSING"
    )
    specification = models.OneToOneField(
        Specification,
        verbose_name="Спецификация",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    cart = models.OneToOneField(
        "product.Cart",
        verbose_name="Корзина",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    requisites = models.ForeignKey(
        Requisites,
        verbose_name="Реквизиты заказа",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    account_requisites = models.ForeignKey(
        AccountRequisites,
        verbose_name="Расчетный счет",
        on_delete=models.PROTECT,
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
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    adress_document = models.ForeignKey(
        RequisitesAddress,
        verbose_name="Адрес для документов",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    motrum_requisites = models.ForeignKey(
        BaseInfoAccountRequisites,
        verbose_name="Реквизиты мотрум ",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    bill_name = models.PositiveIntegerField(
        "Номер счета",
        default=None,
        null=True,
    )
    bill_name_prefix = models.CharField(
        "Префикс номера счета",
        max_length=100, choices=TYPE_ORDER_NAME, default="ОКТ",blank=True,
        null=True,
    )
    bill_file = models.FileField(
        "Фаил счета",
        upload_to=get_document_bill_path,
        blank=True,
        null=True,
        max_length=1000,
    )
    bill_file_no_signature = models.FileField(
        "Фаил счета без печатей",
        upload_to=get_document_bill_path,
        blank=True,
        null=True,
        max_length=1000,
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
        "Фаил акта поставки", upload_to=get_document_bill_path, null=True, default=None, max_length=1000
    )
    marginality = models.FloatField(
        "Маржинальность заказа в %",
        blank=True,
        null=True,
    )
    marginality_sum = models.FloatField(
        "Маржинальность заказа в рублях",
        blank=True,
        null=True,
    )
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return str(self.id)

    @classmethod
    def from_db(cls, db, field_names, values):
        instance = super().from_db(db, field_names, values)

        # save original values, when model is loaded from database,
        # in a separate attribute on the model
        instance._loaded_values = dict(zip(field_names, values))

        return instance

    def save(self, *args, **kwargs):
        from apps.notifications.models import Notification

        print("order-save")

        if not self._state.adding:
            if self._loaded_values["status"] != self.status:
                Notification.add_notification(self.id, "STATUS_ORDERING", None)

            if (
                self._loaded_values["status"] == "PRE-PROCESSING"
                and self.status == "PROCESSING"
            ):
                print("== PRE-PROCESSING and self.status == PROCESSING")
                self.send_email_order_info( "PROCESSING")

        super().save(*args, **kwargs)

    def send_email_order_info(self, types):
        client = self.client
        need_email = False
        data = None
        if client and client.email:
            if types == "PROCESSING":
                need_email = True
                html_message_template = "core/emails/email_get_order_to_client.html"
                categ = CategoryProduct.objects.filter(is_send_email=True)
                print(DOMIAN)
                domian = DOMIAN[:-1]
                
                data = {
                    "categ": categ,
                    "domian": domian,
                }
                print(data)
                subject = f"Заказ в магазине motrum.ru"

        if need_email:
            html_message = loader.render_to_string(
                html_message_template,
                {"context": data},
            )
            print(html_message)

            to_email = client.email
            if IS_TESTING:
                pass
            else:
                test = send_email_message_and_file_alternative(
                    subject, None, to_email, None, html_message
                )
            

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

        (
            pdf_file,
            pdf_name,
            file_path_no_sign,
            version,
            name_bill_to_fullname,
            name_bill_to_fullname_nosign,
        ) = crete_pdf_bill(
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

            self.bill_date_start = datetime.date.today()
            bill_date_start = datetime.date.today()
            data_stop = create_time_stop_specification()
            data_stop = datetime.datetime.strptime(data_stop, "%Y-%m-%d").date()
            self.bill_date_stop = data_stop

            self.bill_file = pdf_file
            self.bill_file_no_signature = file_path_no_sign
            self.bill_sum = self.specification.total_amount
            self.bill_name = pdf_name
            self.marginality = self.specification.marginality
            self.marginality_sum = self.specification.marginality_sum
            if IS_TESTING:
                pass
            else:
                Notification.add_notification(self.id, "DOCUMENT_BILL", pdf_file)
            self._change_reason = "Ручное"
            self.save()

            old_document = OrderDocumentBill.objects.filter(order=self)
            if old_document:
                old_document.update(is_active=False)

            OrderDocumentBill.objects.create(
                order=self,
                bill_name=pdf_name,
                bill_file=pdf_file,
                bill_name_prefix=self.bill_name_prefix,
                bill_date_start=bill_date_start,
                bill_date_stop=data_stop,
                bill_file_no_signature=None,
                bill_sum=self.bill_sum,
                version=version,
                from_index="Б",
                text_name_bill=name_bill_to_fullname,
            )

            OrderDocumentBill.objects.create(
                order=self,
                bill_name=pdf_name,
                bill_name_prefix=self.bill_name_prefix,
                bill_file=None,
                bill_file_no_signature=file_path_no_sign,
                bill_date_start=bill_date_start,
                bill_date_stop=data_stop,
                bill_sum=self.bill_sum,
                version=version,
                from_index="Б",
                text_name_bill_no_sign=name_bill_to_fullname_nosign,
            )
            return self.id
        else:
            return None

    # Получение русского названия статуса в шаблоны
    def get_status_name(self):
        for choice in STATUS_ORDER:
            if choice[0] == self.status:
                return choice[1]
        return ""

    def get_absolute_url_web(self):

        return reverse(
            "client:order_client_one",
            kwargs={
                "pk": self.pk,
            },
        )


# @receiver(pre_save, sender=Order)
# def add_notif_status(sender, instance, **kwargs):
#     from apps.notifications.models import Notification
#     print(instance.status)
#     if update_fields.status:
#         if instance.status != update_fields.status:
#             Notification.add_notification(instance.id, "STATUS_ORDERING",None)


# фаилы счетов все версии
FROM_INDEX = (
    ("-", "Неизвестно"),
    ("Б", "битрикс"),
)


class OrderDocumentBill(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name="Заказ",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    from_index = models.CharField(max_length=500, choices=FROM_INDEX, default="-")

    is_active = models.BooleanField("Активно", default=True)
    bill_name = models.PositiveIntegerField(
        "Номер счета",
        default=None,
        null=True,
    )
    bill_name_prefix = models.CharField(
        "Префикс номера счета",
        max_length=100, choices=STATUS_ORDER, default="ОКТ",blank=True,
        null=True,
    )
    text_name_bill = models.CharField(
        "Текстовое название",
        default=None,
        max_length=1000,
        blank=True,
        null=True,
    )
    bill_file = models.FileField(
        "Фаил счета",
        default=None,
        null=True,
        max_length=1000,
    )
    text_name_bill_no_sign = models.CharField(
        "Текстовое название без подписи",
        default=None,
        max_length=1000,
        blank=True,
        null=True,
    )
    bill_file_no_signature = models.FileField(
        "Фаил счета без печатей",
        default=None,
        null=True,
        max_length=1000,
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
        max_length=1000,
    )
    # name = models.PositiveIntegerField(
    #     "номер",
    #     default=None,
    #     null=True,
    # )
    name = models.CharField(
        "номер",
        default=None,
        max_length=1000,
        blank=True,
        null=True,
    )

    # history = HistoricalRecords(history_change_reason_field=models.TextField(null=True))
    def save(self, *args, **kwargs):
        from apps.notifications.models import Notification
        
        if self.order.client:
            Notification.add_notification(self.order.id, "DOCUMENT_ACT", self.file)

        super().save(*args, **kwargs)
