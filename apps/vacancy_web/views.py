from django.shortcuts import render

from apps.core.models import PhotoEmoloeeInfoWeb
from apps.vacancy_web.models import (
    PhotoEducationInfoWeb,
    PhotoSportsRecreationInfoWeb,
    Vacancy,
    VacancyCategory,
)


# Create your views here.
def vacancy(request):
    title = "Карьера"
    vacancy = Vacancy.objects.filter(is_actual=True)
    category_vacancy = VacancyCategory.objects.filter(is_view=True).order_by("article")
    photo_motrum = PhotoEmoloeeInfoWeb.objects.all()
    photo_education = PhotoEducationInfoWeb.objects.all()
    photo_recreation = PhotoSportsRecreationInfoWeb.objects.all()

    context = {
        "title": title,
        "vacancy": vacancy,
        "category_vacancy": category_vacancy,
        "photo_motrum": photo_motrum,
        "photo_education": photo_education,
        "photo_recreation": photo_recreation,
        "meta_title": f"{title} | Мотрум - автоматизация производства",
    }
    return render(request, "vacancy_web/vacancy_all.html", context)


def vacancy_item(request, slug):
    title = "Вакансия"
    vacancy = Vacancy.objects.get(slug=slug)
    context = {
        "title": title,
        "vacancy": vacancy,
    }

    return render(request, "vacancy_web/vacancy_one.html", context)
