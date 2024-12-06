import threading
from django.db import models


from apps.core.utils_web import get_file_path_slider_web
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
    ("PROMOTE", "Продвижение товара"),
)


class SliderMain(models.Model):
    active = models.BooleanField("Активно", default=True)
    name = models.CharField("Название слайда для админки", max_length=200, unique=True)
    slug = models.CharField(
        max_length=200,
    )
    # title = models.CharField("Заголовок слайда", max_length=200, blank=True, null=True)
    # text = models.CharField("Описание слайда", max_length=200, blank=True, null=True)
    text1 = models.CharField("Текст 1 строка", max_length=200, blank=True, null=True)
    text2 = models.CharField("Текст в обводке", max_length=200, blank=True, null=True)
    icon3 = models.ImageField(
        "Изображение вторая строка текста",
        upload_to=get_file_path_slider_web,
        max_length=255,
        blank=True,
        null=True,
    )
    text4 = models.CharField("Текст 2 строка", max_length=200, blank=True, null=True)

    image = models.ImageField(
        "Изображение левое",
        upload_to=get_file_path_slider_web,
        max_length=255,
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
        max_length=255,
        blank=True,
        null=True,
    )
    link = models.CharField(
        "Ссылка для перехода", max_length=200, blank=True, null=True
    )
    product_promote = models.ForeignKey(
        "product.Product",
        verbose_name="Продвигаемый товар",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )

    type_slider = models.CharField(max_length=7, choices=SLIDER_TYPE, default="MAIN")

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
        "Номер счета клиента", null=True, blank=True, default=0
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

    class Meta:
        verbose_name = "Типы доставки"
        verbose_name_plural = "Типы доставок"

    def __str__(self):
        return self.text
    
    
class IndexInfoWeb(models.Model):
    tech_project = models .SmallIntegerField("реализованных проектов технического зрения")
    modernization = models.SmallIntegerField("модернизировано установок")

    shkaf_upravleniya = models.SmallIntegerField("изготовлено шкафов         управления")
    installation = models.SmallIntegerField("запущенных установок")

    class Meta:
        verbose_name = "Инфа для главной страницы"
        verbose_name_plural = "Инфа для главной страницы"

    def __str__(self):
        return f"Счетчики"



