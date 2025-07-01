from django.utils import timezone
from django.db import models
from django.urls import reverse
from pytils import translit
from django.utils.text import slugify
from django.db import models
from tinymce import models as tinymce_models
from apps.core.utils import get_file_path_add
from apps.core.utils_web import get_file_path_catalog_web, get_file_path_project_web


# Create your models here.
class Project(models.Model):
    company = models.CharField("Компания(не отображается на сайте)", max_length=100,blank=True,
        null=True,)
    name = models.CharField("Название проекта", max_length=200)
    slug = models.SlugField(null=True, max_length=200)
    # short_text = models.CharField("Короткий текст вступление", max_length=500)
    text = models.TextField(
        "Текст открывающий",
        blank=True,
        null=True,
    )
    image_main = models.ImageField(
        "Главное изображение",
        upload_to=get_file_path_project_web,
        max_length=1000,
        null=True,
    )
    is_view_home_web = models.BooleanField("Показывать на главной сайта", default=True)
    category_project = models.ForeignKey(
        "CategoryProject",
        verbose_name="Решение",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    data_create = models.DateField(default=timezone.now, verbose_name="Дата добавления")
    data_project = models.DateField(
        verbose_name="Дата реализации проекта",
        blank=True,
        null=True,
    )
    place_object = models.CharField(
        "Место реализации",
        max_length=500,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.name = " ".join(self.name.split())
            
        if self.slug:
            pass
        else:
            is_project = Project.objects.filter(name=self.name).exists()
            if is_project and self.slug == None:
                project_id = Project.objects.filter(name=self.name).count()
                project_id = int(project_id) + 1
                name = f"{self.name} {project_id}"
            else:
                name = self.name

            slug_text = name
            slugish = translit.translify(slug_text)
            self.slug = slugify(slugish)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "projects_web:project",
            kwargs={
                "project": self.slug,
            },
        )


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        "Изображение", upload_to=get_file_path_project_web, max_length=1000, null=True
    )

    class Meta:
        verbose_name = "Изображение проекта"
        verbose_name_plural = "Изображения проекта"


class ProjectVideo(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    video = models.FileField(
        "Видео", upload_to=get_file_path_project_web, max_length=1000, null=True
    )

    class Meta:
        verbose_name = "Видео проекта"
        verbose_name_plural = "Видео проекта"


class CategoryProject(models.Model):
    name = models.CharField("Название решений", max_length=200)
    slug = models.SlugField(null=True, max_length=100)
    short_name = models.CharField(
        "Короткое название решений",
        max_length=100,
        blank=True,
        null=True,
    )

    # image = models.ImageField(
    #     "Изображение решений",
    #     upload_to=get_file_path_project_web,
    #     max_length=255,
    #     blank=True,
    #     null=True,
    # )

    article = models.PositiveIntegerField(
        "Очередность",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Вид решения"
        verbose_name_plural = "Виды решений"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.name = " ".join(self.name.split())

        slug_text = self.name
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)
        super().save(*args, **kwargs)


class ClientCategoryProject(models.Model):
    name = models.CharField("Название отрасли", max_length=200)
    short_name = models.CharField(
        "Короткое название ",
        max_length=100,
        blank=True,
        null=True,
    )
    slug = models.SlugField(null=True, max_length=100)
    article = models.PositiveIntegerField(
        "Очередность",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Отрасль клиента"
        verbose_name_plural = "Отрасли клиентов"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.name = " ".join(self.name.split())

        slug_text = self.name
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)
        super().save(*args, **kwargs)


class ClientCategoryProjectMarking(models.Model):
    name = models.CharField("Название маркировки", max_length=200)
    short_name = models.CharField(
        "Короткое название решений",
        max_length=100,
        blank=True,
        null=True,
    )
    slug = models.SlugField(null=True, max_length=100)
    article = models.PositiveIntegerField(
        "Очередность",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Маркировка"
        verbose_name_plural = "Маркировка"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.name = " ".join(self.name.split())

        slug_text = self.name
        slugish = translit.translify(slug_text)
        self.slug = slugify(slugish)
        super().save(*args, **kwargs)


class ProjectTextBlock(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    title = models.CharField(
        max_length=2000,
        verbose_name="Заголовок абзаца",
        blank=True,
        null=True,
    )
    # short_text = models.TextField(
    #     "Короткий текст вступление",
    #     blank=True,
    #     null=True,
    # )
    text = tinymce_models.HTMLField(
        "Текст абзаца",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Абзацы проекта"
        verbose_name_plural = "Абзацы проекта"


class ProjectClientCategoryProject(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    client_category = models.ForeignKey(
        ClientCategoryProject,
        verbose_name="Отрасль",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Отрасль"
        verbose_name_plural = "Отрасли"


class ProjectClientCategoryProjectMarking(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    client_category_marking = models.ForeignKey(
        ClientCategoryProjectMarking,
        verbose_name="Маркировка",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Маркировка"
        verbose_name_plural = "Маркировка"
