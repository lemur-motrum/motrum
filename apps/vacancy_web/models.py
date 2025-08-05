from django.db import models
from pytils import translit
from django.utils.text import slugify
from tinymce import models as tinymce_models
from apps.core.utils_web import get_file_path_company_web


# Create your models here.
class PhotoEducationInfoWeb(models.Model):
    image = models.ImageField(
        "Картинка",
        upload_to=get_file_path_company_web,
        max_length=500,
        blank=True,
        null=True,
    )
    article = models.PositiveIntegerField(
        "Очередность",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Фото блок обучение"
        verbose_name_plural = "Фото блок обучение"

    def __str__(self):
        return f"{self.image}"

class PhotoSportsRecreationInfoWeb(models.Model):
    image = models.ImageField(
        "Картинка",
        upload_to=get_file_path_company_web,
        max_length=500,
        blank=True,
        null=True,
    )
    article = models.PositiveIntegerField(
        "Очередность",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Фото блок спорт и отдых"
        verbose_name_plural = "Фото блок спорт и отдых"

    def __str__(self):
        return f"{self.image}"

class VacancyCategory(models.Model):
    name = models.CharField("Название вакансии", max_length=200)
    slug = models.SlugField(null=True, max_length=200)
    is_view = models.BooleanField("Видимость на сайте", default=True)
    article = models.PositiveIntegerField(
        "Очередность",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Категория вакансий"
        verbose_name_plural = "категории вакансий"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.slug == None:
            slug_text = self.name
            slugish = translit.translify(slug_text)
            base_slug = slugify(slugish)
            slug = base_slug
            ModelClass = self.__class__
            counter = 1
            # Проверяем уникальность
            while ModelClass.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


# типы адресов битрикс
# TYPE_PRICE_VACANCY = (
#     ("1","от"),
#     ("2","до"),
#     ("3","без приставки"),
# )
class Vacancy(models.Model):
    name = models.CharField("Название вакансии", max_length=200)
    slug = models.SlugField(null=True, max_length=200)
    is_actual = models.BooleanField("Актуальность", default=True)
    vacancy_category = models.ForeignKey(
        "VacancyCategory",
        verbose_name="Сфера",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    experience = models.CharField(
        "Опыт",
        max_length=200,
        blank=True,
        null=True,
    )
    busyness = models.CharField(
        "Занятость",
        max_length=200,
        blank=True,
        null=True,
    )
    first = models.FloatField(
        "от",
        blank=True,
        null=True,
    )

    last = models.FloatField(
        "до",
        blank=True,
        null=True,
    )
    fixed = models.FloatField(
        "фиксированная сумма",
        blank=True,
        null=True,
    )
    type_payments = models.CharField("Условия выплат", max_length=500,blank=True,
        null=True,)
    # text = models.TextField("Описание текстовое")
    text = tinymce_models.HTMLField(
        "Общее описание",
        blank=True,
        null=True,
    )
    responsibiliti = tinymce_models.HTMLField(
        "Что нужно",
        blank=True,
        null=True,
    )
    requirement = tinymce_models.HTMLField(
        "Что мы приветствуем",
        blank=True,
        null=True,
    )
    conditions = tinymce_models.HTMLField(
        "Мы предлагаем",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.name = " ".join(self.name.split())

        is_vacancy = Vacancy.objects.filter(name=self.name).exists()
        if is_vacancy:
            vacancy_id = Vacancy.objects.filter(name=self.name).count()
            vacancy_id = int(vacancy_id) + 1
            name = f"{self.name} {vacancy_id}"
        else:
            name = self.name

        
        if self.slug == None:
            slug_text = name
            slugish = translit.translify(slug_text)
            base_slug = slugify(slugish)
            slug = base_slug
            ModelClass = self.__class__
            counter = 1
            # Проверяем уникальность
            while ModelClass.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class VacancyPrice(models.Model):
    Vacancy = models.OneToOneField(
        Vacancy,
        verbose_name="Вакансия",
        on_delete=models.CASCADE,
    )
    # type_price = models.CharField(max_length=100, choices=TYPE_PRICE_VACANCY, default="3")
    first = models.FloatField(
        "от",
        blank=True,
        null=True,
    )

    last = models.FloatField(
        "до",
        blank=True,
        null=True,
    )
    fixed = models.FloatField(
        "фиксированная сумма",
        blank=True,
        null=True,
    )
    type_payments = models.CharField("Условия выплат", max_length=500)

    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты"

    def __str__(self):
        return self.type_price


class WorkingConditions(models.Model):
    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
    )
    text = models.CharField("Условие работы", max_length=500)

    class Meta:
        verbose_name = "Условия работы"
        verbose_name_plural = "Условия работы"

    def __str__(self):
        return self.text


class RequirementsVacancy(models.Model):
    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
    )
    text = models.CharField("Требование к кандидату", max_length=500)

    class Meta:
        verbose_name = "Требование к кандидату"
        verbose_name_plural = "Требования к кандидату"

    def __str__(self):
        return self.text


class Responsibilities(models.Model):
    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
    )
    text = models.CharField("Обязанности", max_length=500)

    class Meta:
        verbose_name = "Обязанность кандидата"
        verbose_name_plural = "Обязанности к кандидату"

    def __str__(self):
        return self.text
