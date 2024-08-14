from django.shortcuts import render

from apps.product.models import CategoryProduct


# Create your views here.
def index(request):

    context = {}
    return render(request, "core/index.html", context)


def okt(request):

    context = {}
    return render(request, "core/okt.html", context)


def web(request):
    categories = CategoryProduct.objects.all().order_by("article_name")

    context = {
        "categories": categories,
    }
    return render(request, "core/web.html", context)
