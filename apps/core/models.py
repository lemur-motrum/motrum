from django.db import models


from apps.core.utils_web import get_file_path_project_web, get_file_path_slider_web
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
    ("MAIN", "Только изображение"),
    ("VIDEO", "Видео"),
    ("PHOTO", "Фото право"),
    ("PHOTO_2", "Фото лево"),
    ("PHOTO_2", "Фото лево"),
    ("PROMOTE", "Продвижение товара"),
)


class SliderMain(models.Model):
    active = models.BooleanField("Активно", default=True)
    name = models.CharField("Название слайда для админки", max_length=200, unique=True)
    slug = models.CharField(
        max_length=200,
    )
    title = models.CharField("Заголовок слайда", max_length=200, blank=True, null=True)
    text = models.CharField("Описание слайда", max_length=200, blank=True, null=True)
    image = models.ImageField(
        "Изображение",
        upload_to=get_file_path_slider_web,
        max_length=255,
        blank=True,
        null=True,
    )
    video = models.CharField("Ссылка на видео", max_length=200, blank=True, null=True)
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
        print(self.product_promote)
        if self.product_promote:

            if self.active:
                Product.objects.filter(id=self.product_promote.id).update(promote=True)
            else:
                Product.objects.filter(id=self.product_promote.id).update(promote=False)

        super().save(*args, **kwargs)
