import ast
import json
from re import search
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from apps.product.models import Price, Product
from django.core.paginator import Paginator

from apps.specification.utils import crete_pdf_specification
from .forms import SearchForm
from django.db.models import Q


def specifications(request):
    product_list = Product.objects.select_related(
        "supplier",
        "vendor",
        "category_supplier_all",
        "group_supplier",
        "category_supplier",
        "category",
        "group",
        "price",
        "historic_stock",
    ).all()

    if request.method == "GET":
        form = SearchForm(request.GET)
        if form.is_valid():
            search_input = request.GET.get("search_input")
            if request.GET.get("search_input") != None:
                product_list = product_list.filter(
                    Q(name__icontains=search_input)
                    | Q(article__icontains=search_input)
                    | Q(article_supplier__icontains=search_input)
                    | Q(additional_article_supplier__icontains=search_input)
                )
    else:
        form = SearchForm()

    title = "Услуги"
    paginator = Paginator(product_list, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    num_of_pages = paginator.num_pages
    context = {
        "title": title,
        "products": page_obj,
        "num_of_pages": num_of_pages,
        "form": form,
        "search_input": search_input,
    }
    return render(request, "admin_specification/specification_page.html", context)


def create_specification(request):
    title = "Текущая спецификация"
    cookie = request.COOKIES.get("key")
    if cookie:
        key = json.loads(cookie)
    else:
        key = []

    context = {
        "title": title,
        "specification_items": key,
    }
    return render(request, "admin_specification/specification.html", context)


def save_specification_view_admin(request):
    from apps.specification.models import ProductSpecification, Specification

    received_data = json.loads(request.body)

    # сохранение спецификации
    id_bitrix = received_data["id_bitrix"]  # сюда распарсить значения с фронта
    admin_creator_id = received_data[
        "admin_creator_id"
    ]  # сюда распарсить значения с фронта

    specification = Specification(
        id_bitrix=id_bitrix,
        admin_creator_id=admin_creator_id,
    )
    specification.save()

    # сохранение продуктов для спецификации

    # массив products имитация массива с фронта в него распирсить значения с фронта
    products = received_data["products"]

    # перебор продуктов и сохранение
    for product_item in products:
        product = Product.objects.get(id=product_item["product_id"])
        price = Price.objects.get(prod=product)

        # если цена по запросу взять ее если нет взять цену из бд
        if product_item["price_exclusive"] == True:
            price_one = product_item["price_one"]
        else:
            price_one = price.rub_price_supplier

        price_all = int(price_one) * int(product_item["quantity"])

        product_new = ProductSpecification(
            specification=specification,
            product=product,
            product_currency=price.currency,
            quantity=product_item["quantity"],
            price_one=price_one,
            price_all=price_all,
            price_exclusive=product_item["price_exclusive"],
        )
        product_new.save()
        

    # обновить спецификацию пдф
    pdf = crete_pdf_specification(specification.id)
    Specification.objects.filter(id=specification.id).update(file=pdf)
    print(specification.id)
    out = {"status": "ok", "data": received_data}
    return JsonResponse(out)



