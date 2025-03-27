from re import L
import threading
from django.db import models


from apps.core.utils_web import (
    get_file_path_company_web,
    get_file_path_reviews_web,
    get_file_path_slider_web,
)
from pytils import translit
from django.utils.text import slugify


# Create your models here.
class Currency(models.Model):
    name = models.CharField("Название валюты", max_length=30)
    words_code = models.CharField("Букв. код", max_length=30)
    code = models.SmallIntegerField("Цифр. код")

    class Meta:
        verbose_name = "Валюта"
        verbose_name_plural = "Валюты"

    def __str__(self):
        return self.name


class CurrencyPercent(models.Model):
    percent = models.FloatField("Процент умножения валютных цен")

    class Meta:
        verbose_name = "Процент умножения валютных цен"
        verbose_name_plural = "Процент умножения валютных цен"

    def __str__(self):
        return f"Процент умножения валютных цен: {self.percent}%"

    def save(self, *args, **kwargs):
        from apps.product.models import Price

        super().save(*args, **kwargs)
        price = Price.objects.exclude(currency__words_code="RUB")

        def background_task():
            # Долгосрочная фоновая задача
            for price_one in price:

                price_one._change_reason = "Автоматическое"
                price_one.save()

        daemon_thread = threading.Thread(target=background_task)
        daemon_thread.setDaemon(True)
        daemon_thread.start()


class Vat(models.Model):
    name = models.SmallIntegerField("Процент ндс")

    class Meta:
        verbose_name = "НДС"
        verbose_name_plural = "НДС"

    def __str__(self):
        return str(self.name) + "%"


class CalendarHoliday(models.Model):
    year = models.CharField("Год", max_length=30)
    json_date = models.JSONField("Список выходных из консультанта")

    class Meta:
        verbose_name = "Даты выходных и праздников"


SLIDER_TYPE = (
    ("MAIN", "Лево-изображение. Право-видео или изображение + текст 2 строки"),
    # ("PROMOTE", "Продвижение товара"),
)


class SliderMain(models.Model):
    active = models.BooleanField("Активно", default=True)
    name = models.CharField("Название слайда для админки", max_length=200, unique=True)
    slug = models.CharField(
        max_length=200,
    )
    text1 = models.CharField("Текст 1 строка", max_length=200, blank=True, null=True)
    text2 = models.CharField("Текст в обводке", max_length=200, blank=True, null=True)
    icon3 = models.ImageField(
        "Изображение вторая строка текста",
        upload_to=get_file_path_slider_web,
        max_length=500,
        blank=True,
        null=True,
    )
    text4 = models.CharField("Текст 2 строка", max_length=200, blank=True, null=True)
    
    text_before_block = models.CharField("Текст перед блоком", max_length=200, blank=True, null=True)
    text_after_block = models.CharField("Текст после текста на 2 строке", max_length=200, blank=True, null=True)

    image = models.ImageField(
        "Изображение левое",
        upload_to=get_file_path_slider_web,
        max_length=500,
        blank=True,
        null=True,
    )
    video = models.CharField("Ссылка на видео", max_length=1000, blank=True, null=True)
    video_file = models.FileField(
        "Видео фаилом ",
        upload_to=get_file_path_slider_web,
        blank=True,
        null=True,
    )
    image_right = models.ImageField(
        "Изображение правое",
        upload_to=get_file_path_slider_web,
        max_length=500,
        blank=True,
        null=True,
    )
    link = models.CharField(
        "Ссылка для перехода", max_length=500, blank=True, null=True
    )
    product_promote = models.ForeignKey(
        "product.Product",
        verbose_name="Продвигаемый товар",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    type_slider = models.CharField("Тип слайдера",max_length=7, choices=SLIDER_TYPE, default="MAIN")
    article = models.PositiveIntegerField(
        "Очередность",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Слайдер на главной"
        verbose_name_plural = "Слайдер на главной"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        from apps.product.models import Product

        self.name = self.name.strip()
        self.name = " ".join(self.name.split())
        slug_text = self.name
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)

        if self.product_promote:

            if self.active:
                Product.objects.filter(id=self.product_promote.id).update(promote=True)
            else:
                Product.objects.filter(id=self.product_promote.id).update(promote=False)

        super().save(*args, **kwargs)


class BaseInfo(models.Model):
    from apps.core.utils import get_file_path_add_motrum_base

    stamp = models.ImageField(
        "Печать", upload_to=get_file_path_add_motrum_base, null=True
    )
    signature = models.ImageField(
        "Подпись в документах", upload_to=get_file_path_add_motrum_base, null=True
    )
    full_name_legal_entity = models.CharField(
        "Название компании полностью",
        max_length=300,
    )
    short_name_legal_entity = models.CharField(
        "Название компании кратко",
        max_length=300,
    )
    inn = models.CharField(
        "ИНН",
        max_length=12,
    )
    kpp = models.CharField(
        "КПП",
        max_length=10,
    )
    ogrn = models.CharField("ОГРН", max_length=15, blank=True, null=True)
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
    )
    counter_bill = models.PositiveIntegerField(
        "Номер счета клиента", null=True, blank=True, default=0
    )
    counter_bill_offer = models.PositiveIntegerField(
        "Номер Счет-оферта клиента", null=True, blank=True, default=0
    )

    class Meta:
        verbose_name = "Юридическое лицо"
        verbose_name_plural = "Юридические лица"

    def __str__(self):
        return self.short_name_legal_entity


class BaseInfoAccountRequisites(models.Model):
    is_active = models.BooleanField("Активно", default=True)
    # stamp = models.ImageField("Печать", upload_to=get_file_path_add, null=True)
    # signature = models.ImageField("Подпись в документах", upload_to=get_file_path_add, null=True)
    requisites = models.ForeignKey(
        BaseInfo, verbose_name="Реквизиты", on_delete=models.CASCADE
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
        return self.requisites.short_name_legal_entity


class BaseImage(models.Model):
    from apps.core.utils import get_file_path_add_motrum_base

    logo = models.ImageField(
        "Логотип", upload_to=get_file_path_add_motrum_base, null=True
    )
    vendors = models.ImageField(
        "Поставщики", upload_to=get_file_path_add_motrum_base, null=True
    )

    class Meta:
        verbose_name = "Базовые изображения для документов "
        verbose_name_plural = "Базовые изображения для документов"

    def __str__(self):
        return "Базовые изображения для документов"


class TypeDelivery(models.Model):
    text = models.CharField(
        "Способ доставки ",
        max_length=250,
    )
    text_long = models.CharField(
        "Способ доставки с описанием для документов",
        max_length=1500,
    )

    company_delivery = models.CharField(
        "Компания осуществляющая доставку",
        max_length=250,
        null=True,
        blank=True,
    )
    actual = models.BooleanField("Активно", default=True)

    class Meta:
        verbose_name = "Типы доставки"
        verbose_name_plural = "Типы доставок"

    def __str__(self):
        return self.text


class IndexInfoWeb(models.Model):
    tech_project = models.SmallIntegerField(
        "реализованных проектов технического зрения"
    )
    modernization = models.SmallIntegerField("модернизировано установок")

    shkaf_upravleniya = models.SmallIntegerField(
        "изготовлено шкафов         управления"
    )
    installation = models.SmallIntegerField("запущенных установок")

    class Meta:
        verbose_name = "Мотрум в цифрах главной страницы"
        verbose_name_plural = "Мотрум в цифрах для главной страницы"

    def __str__(self):
        return f"Счетчики"


# {
#     "ID": "187",
#     "ENTITY_ID": "DEAL_STAGE_1",
#     "STATUS_ID": "C1:LOSE",
#     "NAME": "Сделка провалена",
#     "NAME_INIT": "Сделка провалена",
#     "SORT": "70",
#     "SYSTEM": "Y",
#     "COLOR": "#FF5752",
#     "SEMANTICS": "F",
#     "CATEGORY_ID": "1",
#     "EXTRA": {"SEMANTICS": "failure", "COLOR": "#FF5752"},
# }


class StageDealBx(models.Model):
    bitrix_id = models.SmallIntegerField("ID bitrix")
    name = models.CharField(
        "NAME -Имя",
        max_length=250,
        null=True,
        blank=True,
    )
    entity_id = models.CharField(
        "ENTITY_ID - название воронки ",
        max_length=250,
        null=True,
        blank=True,
    )
    category_id = models.CharField(
        "CATEGORY_ID - id воронки ",
        max_length=250,
        null=True,
        blank=True,
    )
    status_id = models.CharField(
        "STATUS_ID - название статуса техническое- пишется в статусе сделки ",
        max_length=250,
        null=True,
        blank=True,
    )
    name_web = models.CharField(
        "Имя на сайте",
        max_length=250,
        null=True,
        blank=True,
    )
    name_web_eng = models.CharField(
        "Имя техническое сат англ",
        max_length=250,
        null=True,
        blank=True,
    )


class SeoTextSolutions(models.Model):
    name_page = models.CharField(
        "название страницы  страницы",
        max_length=250,
        null=True,
        blank=True,
    )
    text = models.CharField(
        "Текст",
        max_length=1500,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Сео для страниц решений"
        verbose_name_plural = "Сео дял страниц решений"

    # def __str__(self):
    #     return f"Счетчики"


class CompanyInfoWeb(models.Model):
    year = models.SmallIntegerField(" лет на рынке год основания – 2012")
    emploee_high = models.SmallIntegerField("высококвалифицированных сотрудника")

    profit = models.SmallIntegerField("оборот группы компаний")
    emploee_engineer = models.SmallIntegerField(" инженерский состав")

    class Meta:
        verbose_name = "Инфа МОТРУМ В ЦИФРАХ страница о компании"
        verbose_name_plural = "Инфа МОТРУМ В ЦИФРАХ страница о компании"

    def __str__(self):
        return f"Счетчики"


class CompanyPrijectAutoInfoWeb(models.Model):
    tech_project = models.SmallIntegerField("установок с техническим зрением")
    shkaf_upravleniya = models.SmallIntegerField("собрано шкафов управления")

    honest_sign = models.SmallIntegerField("линий маркировки «Честный знак»")
    project_all = models.SmallIntegerField(
        "более ___ реализованных проектов по всей России и СН"
    )

    class Meta:
        verbose_name = "Инфа ПРОЕКТЫ КОМПЛЕКСНОЙ АВТОМАТИЗАЦИИ страница о компании"
        verbose_name_plural = (
            "Инфа ПРОЕКТЫ КОМПЛЕКСНОЙ АВТОМАТИЗАЦИИ страница о компании"
        )

    def __str__(self):
        return f"Счетчики"


class ReviewsAutoInfoWeb(models.Model):
    name = models.CharField("Имя сотрудника", max_length=200, blank=True, null=True)
    Legal_entity = models.CharField("Компания", max_length=200, blank=True, null=True)
    text = models.TextField("Текст", blank=True, null=True)
    image = models.ImageField(
        "Картинка",
        upload_to=get_file_path_reviews_web,
        max_length=255,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.Legal_entity}"


class PhotoClientInfoWeb(models.Model):
    image = models.ImageField(
        "Картинка",
        upload_to=get_file_path_company_web,
        max_length=500,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Фото блок клиенты"
        verbose_name_plural = "Фото блок клиенты"

    def __str__(self):
        return f"{self.image}"


class PhotoEmoloeeInfoWeb(models.Model):
    image = models.ImageField(
        "Картинка",
        upload_to=get_file_path_company_web,
        max_length=500,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Фото блок сотрудники"
        verbose_name_plural = "Фото блок сотрудники"

    def __str__(self):
        return f"{self.image}"


class UpdatedCompanyBX24(models.Model):
    company_bx_id = models.IntegerField("company_bx_id")

    def __str__(self):
        return f"{self.image}"
