import json
import os
from django.core import serializers

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from apps.product.models import (
    CategoryProduct,
    GroupProduct,
    Price,
    Product,
)
from django.core.paginator import Paginator

from apps.specification.models import Specification
from apps.specification.utils import crete_pdf_specification
from project.settings import MEDIA_ROOT
from .forms import SearchForm
from django.db.models import Q


def all_categories(request):
    title = "Каталог"
    categories = CategoryProduct.objects.all()

    context = {"title": title, "categories": categories}

    return render(request, "admin_specification/categories.html", context)


def group_product(request, cat):
    categoryes = CategoryProduct.objects.all()
    groups = GroupProduct.objects.select_related("category").filter(category=cat)

    def get_category_name():
        current_cats = [category for category in categoryes if category.pk == cat]
        category_name = current_cats[0].name
        return category_name

    def get_another_category():
        current_cats = [category for category in categoryes if category.pk != cat]
        return current_cats

    context = {
        "title": get_category_name(),
        "categories": get_another_category(),
        "groups": groups,
    }

    return render(request, "admin_specification/group.html", context)


def specifications(request, cat, gr):
    categoryes = CategoryProduct.objects.all()
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
    ).filter(category=cat, group=gr)

    groups = GroupProduct.objects.select_related("category").all()

    def get_category():
        current_cats = [category for category in categoryes if category.pk == cat]
        category = current_cats[0]
        return category

    def get_current_group():
        current_group = [group for group in groups if group.pk == gr]
        return current_group[0]

    def get_another_groups():
        current_group = [
            group for group in groups if group.pk != gr and group.category.pk == cat
        ]
        return current_group

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
    paginator = Paginator(product_list, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    num_of_pages = paginator.num_pages

    context = {
        "title": title,
        "products": page_obj,
        "num_of_pages": num_of_pages,
        "form": form,
        "search_input": search_input,
        "group": get_current_group(),
        "another_groups": get_another_groups(),
        "category": get_category(),
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
    return render(request, "admin_specification/catalog.html", context)


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

    out = {"status": "ok", "data": received_data}
    return JsonResponse(out)


def get_all_specifications(request):
    all_specifications = (
        Specification.objects.select_related(
            "wholesale",
            "admin_creator",
        )
        .all()
        .order_by("pk")
        .reverse()
    )

    media_root = os.path.join(MEDIA_ROOT, "")

    title = "Все спецификации"
    context = {
        "title": title,
        "specifications": all_specifications,
        "media_root": media_root,
    }
    return render(request, "admin_specification/all_specifications.html", context)


def instruments(request, cat):
    category = CategoryProduct.objects.filter(pk=cat)
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
    ).filter(
        category=cat,
    )
    title = category[0].name
    category = category[0]
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

    paginator = Paginator(product_list, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    num_of_pages = paginator.num_pages
    context = {
        "title": title,
        "products": page_obj,
        "num_of_pages": num_of_pages,
        "form": form,
        "search_input": search_input,
        "category": category,
    }

    return render(request, "admin_specification/specification_page.html", context)


def search_product(request):
    data = json.loads(request.body)
    cat = data["category"]
    gr = data["group"]
    value = data["value"]

    if gr == "":
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
        ).filter(category=cat)
    else:
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
        ).filter(category=cat, group=gr)

    product_list = product_list.filter(
        Q(name__icontains=value)
        | Q(article__icontains=value)
        | Q(article_supplier__icontains=value)
        | Q(additional_article_supplier__icontains=value)
    )

    products = serializers.serialize("json", product_list)
    out = {"status": "ok", "products": products}
    return JsonResponse(out)
