from django.shortcuts import render

from apps.core.models import PhotoEmoloeeInfoWeb
from apps.vacancy_web.models import Vacancy


# Create your views here.
def vacancy(request):
    title = "Карьера"
    vacancy = Vacancy.objects.filter(is_actual=True)
    photo_motrum = PhotoEmoloeeInfoWeb.objects.all()

    context = {
        "title": title,
        "vacancy": vacancy,
        "photo_motrum": photo_motrum,
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
