from django.db import models
from pytils import translit
from django.utils.text import slugify

# Create your models here.


class Vacancy(models.Model):
    name = models.CharField("Название вакансии", max_length=200)
    slug = models.SlugField(null=True, max_length=200)
    is_actual = models.BooleanField("Актуальность", default=True)
    text = models.TextField("Описание текстовое")

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

        slug_text = name
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)
        super().save(*args, **kwargs)


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
