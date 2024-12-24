import datetime
import json
from multiprocessing import context
import os
from django.views.decorators.cache import cache_control
from django.core import serializers
from django.db.models import Prefetch, OuterRef
from django.db.models import Sum
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from apps import specification
from apps.client.models import AccountRequisites, Client, Order, RequisitesOtherKpp
from apps.core.bitrix_api import get_info_for_order_bitrix
from apps.core.models import BaseInfo, BaseInfoAccountRequisites, TypeDelivery
from apps.core.utils import get_price_motrum, save_specification
from apps.product.models import (
    Cart,
    CategoryProduct,
    GroupProduct,
    Lot,
    Price,
    Product,
    ProductCart,
    ProductProperty,
    Stock,
    Vendor,
)
from django.core.paginator import Paginator
from django.contrib.auth.decorators import permission_required


from apps.specification.admin import ProductSpecificationAdmin
from apps.specification.api.serializers import SpecificationSerializer
from apps.specification.models import ProductSpecification, Specification

from apps.user.models import AdminUser
from project.settings import MEDIA_ROOT
from .forms import SearchForm
from django.db.models import Q, F, OrderBy, Case, When, Value
from django.db.models.functions import Replace

from django.db.models.functions import Coalesce
from django.db.models.functions import Round
from django.views.decorators.csrf import csrf_exempt


# Рендер главной страницы каталога с пагинацией
@csrf_exempt
@permission_required("specification.add_specification", login_url="/user/login_admin/")
def all_categories(request):
    cart = request.COOKIES.get("cart")
    title = "Каталог"
    categories = (
        CategoryProduct.objects.prefetch_related(Prefetch("groupproduct_set"))
        .all()
        .order_by("article_name")
    )
    vendor = Vendor.objects.filter()
    q_object = Q()
    q_object &= Q(check_to_order=True)
    product_vendor = (
        Product.objects.select_related(
            "vendor",
            "category",
            "group",
        )
        .filter(q_object)
        .distinct("vendor__name")
        .order_by("vendor__name")
        .values("vendor", "vendor__name", "vendor__slug")
    )
    for vendor in product_vendor:
        if vendor["vendor__name"] == None:
            vendor["vendor__name"] = "Не установлен"

    product_list = (
        Product.objects.select_related(
            "supplier",
            "vendor",
            "category",
            "group",
            "price",
            "stock",
        )
        .prefetch_related(
            Prefetch("stock__lot"),
            Prefetch("productproperty_set"),
            Prefetch("price__sale"),
            Prefetch("productcart_set"),
        )
        .filter(check_to_order=True)
        .order_by("pk")
    )

    if cart:
        product_cart_prod = ProductCart.objects.filter(cart=cart, product__isnull=False)
        product_list.annotate(
            id_product_cart=product_cart_prod.filter(product=OuterRef("pk")).values(
                "id",
            ),
        )

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

    if request.GET.get("vendor") != None:
        vendor_urls = request.GET.get("vendor")
        vendor_get = vendor_urls.split(",")
        if "None" in vendor_get:
            if len(vendor_get) > 1:
                vendor_get.remove("None")
                product_list = product_list.filter(
                    Q(
                        vendor__slug=None,
                    )
                    | Q(vendor__slug__in=vendor_get)
                )
            else:
                product_list = product_list.filter(vendor__slug=None)
        else:
            product_list = product_list.filter(vendor__slug__in=vendor_get)
        vendor_url = vendor_urls
    else:
        vendor_url = False

    if request.GET.get("price") != None:
        price_url = request.GET.get("price")
        if price_url == "up":
            product_list = product_list.order_by(
                F("price__rub_price_supplier").asc(nulls_last=True)
            )
        else:
            product_list = product_list.order_by(
                F("price__rub_price_supplier").desc(nulls_last=True)
            )
    else:
        price_url = False

    paginator = Paginator(product_list, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    num_of_pages = paginator.num_pages

    context = {
        "title": title,
        "categories": categories,
        "products": page_obj,
        "num_of_pages": num_of_pages,
        "form": form,
        "product_vendor": product_vendor,
        "vendor_url": vendor_url,
        "price_url": price_url,
    }

    renders = "admin_specification/categories.html"

    return render(request, "admin_specification/categories.html", context)


# Рендер страницы групп товаров с пагинацией
@permission_required("specification.add_specification", login_url="/user/login_admin/")
def group_product(request, cat):

    categoryes = (
        CategoryProduct.objects.prefetch_related(Prefetch("groupproduct_set"))
        .all()
        .order_by("article_name")
    )
    groups = (
        GroupProduct.objects.select_related("category")
        .filter(category=cat)
        .order_by("article_name")
    )

    vendor = Vendor.objects.filter()
    q_object = Q()
    q_object &= Q(check_to_order=True)
    if cat is not None:
        q_object &= Q(category__pk=cat)
    product_vendor = (
        Product.objects.select_related(
            "vendor",
            "category",
            "group",
        )
        .filter(q_object)
        .order_by("vendor__name")
        .distinct("vendor__name")
        .values("vendor", "vendor__name", "vendor__slug")
    )
    for vendor in product_vendor:
        if vendor["vendor__name"] == None:
            vendor["vendor__name"] = "Не установлен"

    product_list = (
        Product.objects.select_related(
            "supplier",
            "vendor",
            "category",
            "group",
            "price",
            "stock",
        )
        .prefetch_related(
            Prefetch("stock__lot"),
            Prefetch("productproperty_set"),
            Prefetch("price__sale"),
        )
        .filter(category=cat, check_to_order=True)
        .order_by("pk")
    )

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

    if request.GET.get("vendor") != None:
        vendor_urls = request.GET.get("vendor")
        vendor_get = vendor_urls.split(",")
        if "None" in vendor_get:
            if len(vendor_get) > 1:
                vendor_get.remove("None")
                product_list = product_list.filter(
                    Q(
                        vendor__slug=None,
                    )
                    | Q(vendor__slug__in=vendor_get)
                )
            else:
                product_list = product_list.filter(vendor__slug=None)
        else:
            product_list = product_list.filter(vendor__slug__in=vendor_get)
        vendor_url = vendor_urls
    else:
        vendor_url = False

    if request.GET.get("price") != None:
        price_url = request.GET.get("price")
        if price_url == "up":
            product_list = product_list.order_by(
                F("price__rub_price_supplier").asc(nulls_last=True)
            )
        else:
            product_list = product_list.order_by(
                F("price__rub_price_supplier").desc(nulls_last=True)
            )
    else:
        price_url = False

    paginator = Paginator(product_list, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    num_of_pages = paginator.num_pages

    def get_category_name():
        current_cats = [category for category in categoryes if category.pk == cat]
        category_name = current_cats[0].name
        return category_name

    def get_another_category():
        current_cats = [category for category in categoryes if category.pk != cat]
        return current_cats

    def get_category():
        current_cats = [category for category in categoryes if category.pk == cat]
        category = current_cats[0]
        return category

    context = {
        "title": get_category_name(),
        "categories": get_another_category(),
        "groups": groups,
        "products": page_obj,
        "num_of_pages": num_of_pages,
        "form": form,
        "category": get_category(),
        "product_vendor": product_vendor,
        "vendor_url": vendor_url,
        "price_url": price_url,
    }

    return render(request, "admin_specification/group.html", context)


# Рендер страницы подгрупп с пагинацией
@permission_required("specification.add_specification", login_url="/user/login_admin/")
def specifications(request, cat, gr):

    categoryes = (
        CategoryProduct.objects.prefetch_related(Prefetch("groupproduct_set"))
        .all()
        .order_by("article_name")
    )
    product_list = (
        Product.objects.select_related(
            "supplier",
            "vendor",
            "category_supplier_all",
            "group_supplier",
            "category_supplier",
            "category",
            "group",
            "price",
            "stock",
        )
        .prefetch_related(
            Prefetch("stock__lot"),
            Prefetch("productproperty_set"),
            Prefetch("price__sale"),
        )
        .filter(check_to_order=True, category=cat, group=gr)
        .order_by("pk")
    )

    vendor = Vendor.objects.filter()
    q_object = Q()
    q_object &= Q(check_to_order=True)
    if cat is not None:
        q_object &= Q(category__pk=cat)
    if gr is not None:
        q_object &= Q(group__pk=gr)

    product_vendor = (
        Product.objects.select_related(
            "vendor",
            "category",
            "group",
        )
        .filter(q_object)
        .order_by("vendor__name")
        .distinct("vendor__name")
        .values("vendor", "vendor__name", "vendor__slug")
    )
    for vendor in product_vendor:
        if vendor["vendor__name"] == None:
            vendor["vendor__name"] = "Не установлен"

    if request.GET.get("vendor") != None:
        vendor_urls = request.GET.get("vendor")
        vendor_get = vendor_urls.split(",")
        if "None" in vendor_get:
            if len(vendor_get) > 1:
                vendor_get.remove("None")
                product_list = product_list.filter(
                    Q(
                        vendor__slug=None,
                    )
                    | Q(vendor__slug__in=vendor_get)
                )
            else:
                product_list = product_list.filter(vendor__slug=None)
        else:
            product_list = product_list.filter(vendor__slug__in=vendor_get)
        vendor_url = vendor_urls
    else:
        vendor_url = False

    if request.GET.get("price") != None:
        price_url = request.GET.get("price")
        if price_url == "up":
            product_list = product_list.order_by(
                F("price__rub_price_supplier").asc(nulls_last=True)
            )
        else:
            product_list = product_list.order_by(
                F("price__rub_price_supplier").desc(nulls_last=True)
            )
    else:
        price_url = False

    groups = (
        GroupProduct.objects.select_related("category").all().order_by("article_name")
    )

    supplers = []

    for product in product_list:
        supplers.append(product.supplier)

    def get_unique_supplers():
        list_of_unique_supplers = []
        unique_supplers = set(supplers)

        for suppler in unique_supplers:
            list_of_unique_supplers.append(suppler)

        return list_of_unique_supplers

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
        "supplers": get_unique_supplers(),
        "product_vendor": product_vendor,
        "vendor_url": vendor_url,
        "price_url": price_url,
    }
    return render(request, "admin_specification/specification_page.html", context)


# рендер страницы корзины
# @cache_control(max_age=3600)
@csrf_exempt
@permission_required("specification.add_specification", login_url="/user/login_admin/")
def create_specification(request):
    cart = request.COOKIES.get("cart")
    type_save_cookee = request.COOKIES.get("type_save")
    post_data_bx_id = request.COOKIES.get("bitrix_id_order")

    # если есть корзина
    if cart != None:
        cart_qs = Cart.objects.get(id=cart)
        if cart_qs.client:
            discount_client = Client.objects.filter(id=cart_qs.client.id)

        product_cart_list = ProductCart.objects.filter(
            cart=cart, product__isnull=False
        ).values_list("product__id")

        product_cart_prod = ProductCart.objects.filter(cart=cart, product__isnull=False)
        product_cart = ProductCart.objects.filter(cart=cart)

        # изменение спецификации
        if type_save_cookee != "new":
            # try:
            specification = Specification.objects.get(cart=cart)
            order = Order.objects.get(specification=specification)
            client_req = order.account_requisites
            requisites_kpp = client_req.requisitesKpp
            requisites = order.requisites
            client_req_all = AccountRequisites.objects.filter(
                requisitesKpp__requisites=requisites
            )

            product_specification = ProductSpecification.objects.filter(
                specification=specification
            )

            mortum_req = BaseInfoAccountRequisites.objects.all().select_related(
                "requisites"
            )

            title = f"Заказ № {order.id}"
            order = Order.objects.get(specification=specification)

            # список товаров без записи в окт которые были в спецификации
            product_new = (
                ProductSpecification.objects.filter(
                    specification=specification,
                    # product=None,
                    product_new_article__isnull=False,
                )
                .annotate(
                    id_product_spesif=F("id"),
                    product_new_cart_vendor=product_cart.filter(
                        id=OuterRef("id_cart")
                    ).values(
                        "vendor",
                    ),
                    product_new_cart=product_cart.filter(id=OuterRef("id_cart")).values(
                        "product_new",
                    ),
                    product_new_article_cart=product_cart.filter(
                        id=OuterRef("id_cart")
                    ).values(
                        "product_new_article",
                    ),
                    id_product_cart=product_cart.filter(id=OuterRef("id_cart")).values(
                        "id",
                    ),
                    product_new_price=product_cart.filter(
                        id=OuterRef("id_cart")
                    ).values(
                        "product_new_price",
                    ),
                    product_new_sale_motrum=product_cart.filter(
                        id=OuterRef("id_cart")
                    ).values(
                        "product_new_sale_motrum",
                    ),
                )
                .annotate(
                    price_motrum=Case(
                        When(
                            product_new_sale_motrum=None,
                            then=("product_new_price"),
                        ),
                        When(
                            product_new_sale_motrum__isnull=False,
                            then=Round(
                                F("product_new_price")
                                - (
                                    F("product_new_price")
                                    / 100
                                    * (F("product_new_sale_motrum"))
                                ),
                                2,
                            ),
                        ),
                    ),
                )
                .order_by("id_product_cart")
            )
            product_new_value_id = product_new.values_list("id_product_cart")

            # список товаров без щаписи в окт которые новые еще на записанны
            product_new_more = (
                ProductCart.objects.filter(
                    cart=cart,
                    #    product=None
                    product_new_article__isnull=False,
                )
                .exclude(id__in=product_new_value_id)
                .annotate(
                    price_motrum=Case(
                        When(
                            product_new_sale_motrum=None,
                            then=("product_new_price"),
                        ),
                        When(
                            product_new_sale_motrum__isnull=False,
                            then=Round(
                                F("product_new_price")
                                - (
                                    F("product_new_price")
                                    / 100
                                    * (F("product_new_sale_motrum"))
                                ),
                                2,
                            ),
                        ),
                    ),
                )
                .order_by("id")
            )
            update_spesif = True

        # новая спецификация
        else:
            # except Specification.DoesNotExist:

            try:
                # если корзина без заказа
                order = Order.objects.get(cart=cart)
                specification = None
                product_new = (
                    ProductCart.objects.filter(cart=cart, product=None)
                    .annotate(
                        price_motrum=Case(
                            When(
                                product_new_sale_motrum=None,
                                then=("product_new_price"),
                            ),
                            When(
                                product_new_sale_motrum__isnull=False,
                                then=Round(
                                    F("product_new_price")
                                    - (
                                        F("product_new_price")
                                        / 100
                                        * (F("product_new_sale_motrum"))
                                    ),
                                    2,
                                ),
                            ),
                        ),
                    )
                    .order_by("id")
                )
                product_specification = ProductSpecification.objects.filter(
                    specification=0
                )

                mortum_req = BaseInfoAccountRequisites.objects.all().select_related(
                    "requisites"
                )

                if order.account_requisites:
                    requisites = order.requisites
                    req_kpp = RequisitesOtherKpp.objects.filter(
                        requisites=requisites
                    ).values("id")

                    client_req_all = AccountRequisites.objects.filter(
                        requisitesKpp__in=req_kpp
                    )
                else:
                    client_req_all = None

                if order.requisites:
                    client_req = order.account_requisites
                else:
                    client_req = None

                title = "Новый заказ"

                update_spesif = False
                product_new_more = None

            except Order.DoesNotExist:
                specification = None
                product_spes_list = ProductSpecification.objects.filter(
                    specification=specification
                ).values_list("product__id")
                product_specification = ProductSpecification.objects.filter(
                    specification=specification
                )
                mortum_req = BaseInfoAccountRequisites.objects.all().select_related(
                    "requisites"
                )
                title = "Новый заказ"
                order = None

                # товары без записи в окт
                product_new = (
                    ProductCart.objects.filter(cart=cart, product=None)
                    .annotate(
                        price_motrum=Case(
                            When(
                                product_new_sale_motrum=None,
                                then=("product_new_price"),
                            ),
                            When(
                                product_new_sale_motrum__isnull=False,
                                then=Round(
                                    F("product_new_price")
                                    - (
                                        F("product_new_price")
                                        / 100
                                        * (F("product_new_sale_motrum"))
                                    ),
                                    2,
                                ),
                            ),
                        ),
                    )
                    .order_by("id")
                )

                product_new_more = None
                update_spesif = False
                client_req = None
                client_req_all = None

        # продукты которые есть в окт в корзине

        product = (
            Product.objects.filter(id__in=product_cart_list)
            .select_related(
                "supplier",
                "vendor",
                "category",
                "group",
                "price",
                "stock",
                "category_supplier_all",
                "group_supplier",
                "category_supplier",
                # "stock__lot",
            )
            .prefetch_related(
                Prefetch("stock__lot"),
                Prefetch("productproperty_set"),
                Prefetch("price__sale"),
            )
            .annotate(
                quantity=product_cart_prod.filter(product=OuterRef("pk")).values(
                    "quantity",
                ),
                id_product_cart=product_cart_prod.filter(product=OuterRef("pk")).values(
                    "id",
                ),
                id_product_spesif=product_specification.filter(
                    product=OuterRef("pk")
                ).values(
                    "id",
                ),
                old_price_one=product_specification.filter(
                    product=OuterRef("pk")
                ).values(
                    "price_one",
                ),
                old_extra_discount=product_specification.filter(
                    product=OuterRef("pk")
                ).values(
                    "extra_discount",
                ),
                old_price_one_full=Case(
                    When(old_extra_discount=None, then="old_price_one"),
                    When(
                        old_extra_discount__isnull=False,
                        then=Round(
                            F("old_price_one") / (1 - F("old_extra_discount") / 100),
                            2,
                        ),
                    ),
                ),
                old_price_one_motrum=product_specification.filter(
                    product=OuterRef("pk")
                ).values(
                    "price_one_motrum",
                ),
                old_date=product_specification.filter(product=OuterRef("pk")).values(
                    "specification__date_update",
                ),
                comment=product_specification.filter(product=OuterRef("pk")).values(
                    "comment",
                ),
                text_delivery=product_specification.filter(
                    product=OuterRef("pk")
                ).values(
                    "text_delivery",
                ),
                date_delivery=product_specification.filter(
                    product=OuterRef("pk")
                ).values(
                    "date_delivery",
                ),
                is_prise=product_cart_prod.filter(product=OuterRef("pk")).values(
                    "product__price",
                ),
                actual_price=F("price__rub_price_supplier"),
                date_delivery_bill=product_specification.filter(
                    product=OuterRef("pk")
                ).values(
                    "date_delivery_bill",
                ),
                sale_motrum=product_cart_prod.filter(product=OuterRef("pk")).values(
                    "product_sale_motrum",
                ),
                price_cart=product_cart_prod.filter(product=OuterRef("pk")).values(
                    "product_price",
                ),
                price_motrum=Case(
                    When(sale_motrum=None, then="actual_price"),
                    When(
                        sale_motrum__isnull=False,
                        then=Round(
                            F("price_cart")
                            - (F("price_cart") / 100 * F("sale_motrum")),
                            2,
                        ),
                    ),
                ),
                # price_motrum_okt = Round(
                #             F("price_cart") - (F("price_cart")/100 * F("sale_motrum")),
                #             2,
                #         ),
            )
            # .order_by("id_product_cart")
        )

    # корзины нет
    else:

        client_req_all = None
        client_req = None
        mortum_req = None
        title = "Новый заказ"
        product = None
        product_new = None
        cart = None
        update_spesif = False
        product_new_more = None
        specification = None
        order = None

    current_date = datetime.date.today().isoformat()
    hard_upd = False
    if type_save_cookee == "new":
        bill_upd = False
        if order:
            if order.requisites.contract:
                title = f"Новый заказ: счет + спецификация"
                type_save = "счет + спецификация"
            else:
                title = f"Новый заказ: счет-оферта"
                type_save = "счет-оферта"
        else:
            title = f"Новый заказ"
            type_save = ""

    elif type_save_cookee == "update":
        bill_upd = True
        title = f"Заказ № {order.id} - изменение счета № {order.bill_name} "
        type_save = " изменения"

    elif type_save_cookee == "hard_update":
        bill_upd = False
        hard_upd = True
        # title = f"Заказ № {order.id} - новый счет"
        if order.requisites.contract:
            title = f"Заказ № {order.id}: счет + спецификация"
            type_save = "счет + спецификация"
        else:
            title = f"Заказ № {order.id}: счет-оферта"
            type_save = " счет-оферта"
    else:
        type_save_cookee = "new"
        bill_upd = False
        title = f"Новый заказ"
        type_save = "счет"
    type_delivery = TypeDelivery.objects.all()
    vendor = Vendor.objects.all().order_by("name")
    context = {
        "title": title,
        "product": product,
        "product_new": product_new,
        "cart": cart,
        "request": request,
        "current_date": current_date,
        "update_spesif": update_spesif,
        "product_new_more": product_new_more,
        "specification": specification,
        "mortum_req": mortum_req,
        "order": order,
        "client_req": client_req,
        "client_req_all": client_req_all,
        "bill_upd": bill_upd,
        "vendor": vendor,
        "type_save": type_save,
        "type_delivery": type_delivery,
        "type_save_cookee": type_save_cookee,
        "hard_upd": hard_upd,
        "post_data_bx_id": post_data_bx_id,
    }

    return render(request, "admin_specification/catalog.html", context)


@permission_required("specification.add_specification", login_url="/user/login_admin/")
def update_order(request):
    pass


# Вьюха для сохранения спецификации
@permission_required("specification.add_specification", login_url="/user/login_admin/")
def save_specification_view_admin(request):
    from apps.specification.models import ProductSpecification, Specification

    received_data = json.loads(request.body)

    # сохранение спецификации
    save_specification(received_data, request)

    out = {"status": "ok", "data": received_data}
    return JsonResponse(out)


# рендер страницы со всеми спецификациями
@csrf_exempt
@permission_required(
    "specification.add_specification",
    login_url="/user/login_admin/",
)
def get_all_specifications(request):
    print(1111111111111111)
    print(request.COOKIES)
    print(request.META["HTTP_SEC_FETCH_DEST"])
    cd = []
    post_data_bx_id = "post_data_bx_id"
    if "POST" in request.method:
        post_data = request.POST
        post_data_bx_id = post_data.get("PLACEMENT_OPTIONS")

    q_object = Q()
    # фильтрация по админу
    user_admin = AdminUser.objects.get(user=request.user)
    user_admin_type = user_admin.admin_type
    if user_admin_type == "ALL":
        superuser = True
    elif user_admin_type == "BASE":
        all_specifications = all_specifications.filter(admin_creator_id=request.user.id)
        q_object &= Q(admin_creator_id=request.user.id)
        superuser = False
    # фильтрация если из битрикс
    http_frame = False
    bitrix_id_order = None
    if request.META["HTTP_SEC_FETCH_DEST"] == "iframe":
        print(request.META["HTTP_SEC_FETCH_DEST"])
        bitrix_id_order = request.COOKIES["bitrix_id_order"]
        http_frame = True
        print(bitrix_id_order)
        q_object &= Q(id_bitrix=int(bitrix_id_order))

    all_specifications = (
        Specification.objects.filter(admin_creator__isnull=False)
        .select_related("admin_creator", "cart")
        .prefetch_related(
            Prefetch("order"),
        )
        .filter(q_object)
        .order_by("tag_stop", "date_update", "id")
        .reverse()
    )
    print(q_object)
    print(all_specifications)

    media_root = os.path.join(MEDIA_ROOT, "")

    title = "Все заказы"

    sort_specif = request.GET.get("specification")
    if sort_specif:
        sort_specif = True
    else:
        sort_specif = False

    context = {
        "title": title,
        "specifications": all_specifications,
        "media_root": media_root,
        "sort_specif": sort_specif,
        "superuser": superuser,
        "post_data_bx_id": post_data_bx_id,
        "bitrix_id_order": bitrix_id_order,
        "http_frame": http_frame,
    }

    return render(request, "admin_specification/all_specifications.html", context)


@csrf_exempt
@permission_required(
    "specification.add_specification",
    login_url="/user/login_admin/",
)
def one_specifications(request, pk):
    user_admin = AdminUser.objects.get(user=request.user)
    user_admin_type = user_admin.admin_type
    if user_admin_type == "ALL":
        admin_king = True
    elif user_admin_type == "BASE":
        admin_king = False

    specification = Specification.objects.get(pk=pk)
    product_specification_list = ProductSpecification.objects.filter(
        specification=specification
    ).values_list("product__id")

    product_specification = (
        ProductSpecification.objects.filter(specification=specification)
        .select_related(
            "product",
        )
        .annotate(
            marja=Round(
                F("price_all") - F("price_all_motrum"),
                2,
            ),
        )
        .order_by("id")
        .prefetch_related(Prefetch("product__price"))
    )
    totals = product_specification.aggregate(
        all_sum=Sum("price_all"),
        all_sum_motrum=Sum("price_all_motrum"),
        all_sum_marja=Sum("marja"),
        all_sum_quantity=Sum("quantity"),
    )
    order = Order.objects.get(specification=specification)

    title = "Просмотр заказа"
    context = {
        "title": title,
        "specification": specification,
        "product_specification": product_specification,
        "order": order,
        "admin_king": admin_king,
        "totals": totals,
    }

    return render(request, "admin_specification/one_specifications.html", context)


# рендер страницы товаров у которых есть категория, но нет групп
@permission_required("specification.add_specification", login_url="/user/login_admin/")
def instruments(request, cat):

    category = (
        CategoryProduct.objects.prefetch_related(Prefetch("groupproduct_set"))
        .filter(pk=cat)
        .order_by("article_name")
    )

    vendor = Vendor.objects.filter()
    q_object = Q()
    q_object &= Q(check_to_order=True)
    if cat is not None:
        q_object &= Q(category__pk=cat)
    product_vendor = (
        Product.objects.select_related(
            "vendor",
            "category",
            "group",
        )
        .filter(q_object)
        .order_by("vendor__name")
        .distinct("vendor__name")
        .values("vendor", "vendor__name", "vendor__slug")
    )
    for vendor in product_vendor:
        if vendor["vendor__name"] == None:
            vendor["vendor__name"] = "Не установлен"

    product_list = (
        Product.objects.select_related(
            "supplier",
            "vendor",
            "category",
            "group",
            "price",
            "stock",
        )
        .prefetch_related(
            Prefetch("stock__lot"),
            Prefetch("productproperty_set"),
            Prefetch("price__sale"),
        )
        .filter(
            check_to_order=True,
            category=cat,
        )
        # .filter(check_to_order=True)
        .order_by("pk")
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

    # if request.GET.get("vendor") != None:
    #     vendor_urls = request.GET.get("vendor")
    #     vendor_get = vendor_urls.split(",")
    #
    #     product_list = product_list.filter(vendor__slug__in=vendor_get)
    #     vendor_url = vendor_urls
    # else:
    #     vendor_url = False
    if request.GET.get("vendor") != None:
        vendor_urls = request.GET.get("vendor")
        vendor_get = vendor_urls.split(",")
        if "None" in vendor_get:
            if len(vendor_get) > 1:
                vendor_get.remove("None")
                product_list = product_list.filter(
                    Q(
                        vendor__slug=None,
                    )
                    | Q(vendor__slug__in=vendor_get)
                )
            else:
                product_list = product_list.filter(vendor__slug=None)
        else:
            product_list = product_list.filter(vendor__slug__in=vendor_get)
        vendor_url = vendor_urls
    else:
        vendor_url = False

    if request.GET.get("price") != None:
        price_url = request.GET.get("price")
        if price_url == "up":
            product_list = product_list.order_by(
                F("price__rub_price_supplier").asc(nulls_last=True)
            )
        else:
            product_list = product_list.order_by(
                F("price__rub_price_supplier").desc(nulls_last=True)
            )
    supplers = []

    for product in product_list:
        supplers.append(product.supplier)

    def get_unique_supplers():
        list_of_unique_supplers = []
        unique_supplers = set(supplers)

        for suppler in unique_supplers:
            list_of_unique_supplers.append(suppler)

        return list_of_unique_supplers

    if request.POST.get("numpage"):
        paginator = 312
    else:
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
        "supplers": get_unique_supplers(),
        "product_vendor": product_vendor,
        "vendor_url": vendor_url,
    }

    return render(request, "admin_specification/specification_page.html", context)


# Вьюха для аякс поиска, подзагрузка товаров при скролле вниз
@permission_required("specification.add_specification", login_url="/user/login_admin/")
def search_product(request):
    data = json.loads(request.body)
    cat = data["category"]
    gr = data["group"]
    value = data["value"]
    start = data["start"]
    counter = data["counter"]

    if gr == "" and cat == "":
        product_list = Product.objects.select_related(
            "supplier",
            "vendor",
            "category",
            "group",
        ).filter(check_to_order=True)
    elif gr == "":
        product_list = (
            Product.objects.select_related(
                "supplier",
                "vendor",
                "category",
                "group",
            )
            .filter(category=cat)
            .filter(check_to_order=True)
            .order_by("pk")
        )
    else:
        product_list = (
            Product.objects.select_related(
                "supplier",
                "vendor",
                "category",
                "group",
                "price",
                "stock",
            )
            .filter(category=cat, group=gr)
            .filter(check_to_order=True)
            .order_by("pk")
        )
    search_input = value.split(" ")
    # product_list = product_list.filter(
    #     Q(name__icontains=value)
    #     | Q(article__icontains=value)
    #     | Q(article_supplier__icontains=value)
    #     | Q(additional_article_supplier__icontains=value)
    # )
    product_list = product_list.filter(
        Q(name__icontains=search_input[0])
        | Q(article__icontains=search_input[0])
        | Q(article_supplier__icontains=search_input[0])
        | Q(additional_article_supplier__icontains=search_input[0])
    )
    for search_item in search_input[1:]:
        product_list = product_list.filter(
            Q(name__icontains=search_item)
            | Q(article__icontains=search_item)
            | Q(article_supplier__icontains=search_item)
            | Q(additional_article_supplier__icontains=search_item)
        )

    items = product_list[start:counter]

    products = serializers.serialize("json", items)
    out = {"status": "ok", "products": products}
    return JsonResponse(out)


# Вьюха логики при нажатии на кнопку "Загрузить ещё"
@permission_required("specification.add_specification", login_url="/user/login_admin/")
def load_products(request):

    data = json.loads(request.body)
    cat = data["category"]
    gr = data["group"]
    page_num = data["pageNum"]
    url_params = data["urlParams"]
    price_url = data["priceUrl"]

    if page_num == "":
        start_point = 9
    else:
        start_point = int(page_num) * 9

    endpoint_product = start_point + 9

    if gr == "" and cat == "":
        product_list = (
            Product.objects.prefetch_related(
                "supplier",
                "vendor",
                "category",
                "group",
                "price",
                "stock",
            )
            .prefetch_related(
                Prefetch("stock__lot"),
                Prefetch("productproperty_set"),
                Prefetch("price__sale"),
            )
            .filter(check_to_order=True)
            .order_by("pk")
        )

    elif gr == "":
        product_list = (
            Product.objects.prefetch_related(
                "supplier",
                "vendor",
                "category",
                "group",
                "price",
                "stock",
            )
            .prefetch_related(
                Prefetch("stock__lot"),
                Prefetch("productproperty_set"),
                Prefetch("price__sale"),
            )
            .filter(check_to_order=True, category=cat)
            # .filter(check_to_order=True)
            .order_by("pk")
        )

    else:
        product_list = (
            Product.objects.select_related(
                "supplier",
                "vendor",
                "category",
                "group",
                "price",
                "stock",
            )
            .prefetch_related(
                Prefetch("stock__lot"),
                Prefetch("productproperty_set"),
                Prefetch("price__sale"),
            )
            .filter(check_to_order=True, category=cat, group=gr)
            # .filter(check_to_order=True)
            .order_by("pk")
        )

    if url_params != None:
        product_list = product_list.filter(vendor__slug__in=url_params)

    if price_url != None:
        if price_url == "up":
            product_list = product_list.order_by(
                F("price__rub_price_supplier").asc(nulls_last=True)
            )
        else:
            product_list = product_list.order_by(
                F("price__rub_price_supplier").desc(nulls_last=True)
            )

    items = product_list[start_point:endpoint_product]

    products = []

    for product_elem in items:

        try:
            price_all = Price.objects.get(prod=product_elem.pk)
            price = price_all.rub_price_supplier
            price_suppler = price_all.price_motrum

            discount_item = get_price_motrum(
                product_elem.category_supplier,
                product_elem.group_supplier,
                product_elem.vendor,
                price,
                product_elem.category_supplier_all,
                product_elem.supplier,
            )[1]

            if discount_item == None:
                discount = None
            else:
                discount = discount_item.percent
        except Price.DoesNotExist:
            price_all = None
            price = None
            price_suppler = 0
            discount = None

        chars = ProductProperty.objects.filter(product=product_elem.pk)
        try:
            stock_item = Stock.objects.get(prod=product_elem.pk)
            lotname = stock_item.lot.name_shorts

            if stock_item.is_one_sale == True:
                product_multiplicity = 1
            else:
                product_multiplicity = Stock.objects.get(
                    prod=product_elem.pk
                ).order_multiplicity

        except:
            stock_item = None
            lotname = None
            product_multiplicity = 1

        name = product_elem.name
        pk = product_elem.pk
        article = product_elem.article_supplier
        saler_article = product_elem.article_supplier
        supplier_name = product_elem.supplier.name
        if product_elem.vendor != None:
            vendor_name = product_elem.vendor.name
        else:
            vendor_name = ""

        if stock_item != None:
            stock = 1
            stok_to_order = stock_item.to_order
            stock_supplier = stock_item.stock_supplier_unit
            stock_motrum = stock_item.stock_motrum
            data_update = str(price_all.data_update)
            transit_count = stock_item.transit_count
            data_transit = str(stock_item.data_transit)
            is_one_sale = stock_item.is_one_sale
            lot_complect = stock_item.lot_complect
        else:
            stock = 0
            stok_to_order = 0
            stock_supplier = 0
            stock_motrum = 0
            data_update = 0
            transit_count = 0
            data_transit = 0
            is_one_sale = 0
            lot_complect = 0

        characteristics = []
        for char in chars:
            characteristics.append(char.value)

        product = {
            "name": name,
            "stock": stock,
            "stock_to_order": stok_to_order,
            "stock_supplier": stock_supplier,
            "stock_motrum": stock_motrum,
            "data_update": data_update,
            "transit_count": transit_count,
            "data_transit": data_transit,
            "lot": lotname,
            "pk": pk,
            "article": article,
            "saler_article": saler_article,
            "price": price,
            "chars": characteristics,
            "price_suppler": price_suppler,
            "discount": discount,
            "multiplicity": product_multiplicity,
            "supplier": supplier_name,
            "vendor": vendor_name,
            "is_one_sale": is_one_sale,
            "lot_complect": lot_complect,
        }
        products.append(product)

    current_products = json.dumps(products)
    out = {"status": "ok", "products": current_products}
    return JsonResponse(out, safe=False)


# исторические записи для страниц история
@permission_required("specification.add_specification", login_url="/user/login_admin/")
def history_admin(request, pk):
    from apps.specification.admin import SpecificationAdmin
    from django.contrib.admin.utils import unquote
    from itertools import chain

    specification = Specification.objects.get(pk=pk)
    model = Specification
    opts = model._meta
    app_label = opts.app_label
    pk_name = opts.pk.attname
    history = getattr(model, model._meta.simple_history_manager_attribute)
    object_id = str(pk)

    try:
        product_id_ex = ProductSpecification.objects.filter(specification=pk).last()
        product_id = ProductSpecification.objects.filter(specification=pk)

    except ProductSpecification.DoesNotExist:
        product_id = None

    historical_records_product = []
    if product_id != None:
        for item in product_id:
            item_list = ProductSpecificationAdmin.history_view(
                ProductSpecification, request, item.id, extra_context=None
            )
            if historical_records_product == []:
                historical_records_product = item_list
            else:
                historical_records_product = list(
                    chain(
                        historical_records_product,
                        item_list,
                    )
                )
    deleted_prod = ProductSpecification.history.filter(
        history_type="-", specification_id=pk
    )

    historical_records_product2 = []
    id_old_prod = []
    for item2 in deleted_prod:
        id_old_prod.append(item2.id)
        item_list = ProductSpecificationAdmin.history_view(
            ProductSpecification, request, item2.id, extra_context=None
        )

        if historical_records_product2 == []:
            historical_records_product2 = item_list
        else:
            historical_records_product2 = list(
                chain(
                    historical_records_product2,
                    item_list,
                )
            )

    historical_records = SpecificationAdmin.get_history_queryset(
        SpecificationAdmin, request, history, pk_name, object_id
    )

    history_list_display = SpecificationAdmin.get_history_list_display(
        SpecificationAdmin, request
    )

    for history_list_entry in history_list_display:
        value_for_entry = getattr(SpecificationAdmin, history_list_entry, None)
        if value_for_entry and callable(value_for_entry):
            for record in historical_records:
                setattr(record, history_list_entry, value_for_entry(record))

    from simple_history.template_utils import HistoricalRecordContextHelper

    previous = None
    for current in historical_records:
        if previous is None:
            previous = current
            continue

        delta = previous.diff_against(current, foreign_keys_are_objs=True)

        helper = HistoricalRecordContextHelper(Specification, previous)
        previous.history_delta_changes = helper.context_for_delta_changes(delta)

        previous = current

    result_list = list(
        chain(
            historical_records,
            historical_records_product,
            historical_records_product2,
        )
    )

    def get_date(element):
        return element.history_date

    result_list_sorted = result_list.sort(key=get_date, reverse=True)

    context = {
        "specification": specification,
        "historical_records": result_list,
        "app_label": app_label,
        "opts": opts,
        "history_list_display": history_list_display,
    }

    extra_kwargs = {}

    return SpecificationAdmin.render_history_view(
        SpecificationAdmin,
        request,
        "admin_specification/history_admin.html",
        context,
        **extra_kwargs,
    )

    # context = {
    #         "title": "dsdfsd",

    #     }

    # return render(request, "admin_specification/history_admin.html", context)


@permission_required("specification.add_specification", login_url="/user/login_admin/")
def history_admin_bill(request, pk):
    from simple_history.template_utils import HistoricalRecordContextHelper

    order = Order.objects.get(pk=pk)
    historical_records = order.history.all()
    previous = None
    for current in historical_records:
        if previous is None:
            previous = current
            continue

        delta = previous.diff_against(current, foreign_keys_are_objs=True)

        helper = HistoricalRecordContextHelper(Order, previous)
        previous.history_delta_changes = helper.context_for_delta_changes(delta)

        previous = current

    context = {
        "historical_records": historical_records,
        "history_list_display": None,
    }

    return render(request, "admin_specification/history_admin_bill.html", context)


def error_b24(request, error):
    context = {"error": 1}
    return render(request, "admin_specification/error.html", context)


@csrf_exempt
@permission_required("specification.add_specification", login_url="/user/login_admin/")
def bx_start_page(request):
    print("bx_start_page")
    print(request)

    # bx_id_order = request.GET.get("bitrix_id_order")
    # order = Order.objects.get(id_bitrix=int(bx_id_order))
    # context = {"cart": order.cart.id, "spes": order.specification.id}

    return render(request, "admin_specification/bx_start.html", context)


@csrf_exempt
@permission_required("specification.add_specification", login_url="/user/login_admin/")
def bx_save_start_info(request):
    if "POST" in request.method:
        post_data = request.POST
        post_data_bx_place = post_data.get("PLACEMENT")
        post_data_bx_id = post_data.get("PLACEMENT_OPTIONS")
        post_data_bx_id = json.loads(post_data_bx_id)
        post_data_bx_id = post_data_bx_id["ID"]
        
        if post_data_bx_place == "CRM_DEAL_DETAIL_TAB":
            next_url, context, error = get_info_for_order_bitrix(
                post_data_bx_id, request
            )
            print(next_url, context, error)
        if error:
            print("ERR")
            response = render(
                    request,
                    "admin_specification/error.html",
                    context,
                )
            response.set_cookie(
                "bitrix_id_order",
                post_data_bx_id,
                max_age=2629800,
                samesite="None",
                secure=True,
            )
            
            return response
        else:
            if context["type_save"] == "new" or context["spes"] == None:
                response = HttpResponseRedirect(
                    "/admin_specification/current_specification/"
                )
                
                response.set_cookie(
                    "type_save",
                    "new",
                    max_age=2629800,
                    samesite="None",
                    secure=True,
                )
            else:
                response = render(
                    request,
                    next_url,
                    context={
                        "cart": context["cart"],
                        "spes": context["spes"],
                        "serializer": context["serializer"],
                        "type_save": context["type_save"],
                    },
                )
            print(11111)
            response.set_cookie(
                "bitrix_id_order",
                post_data_bx_id,
                max_age=2629800,
                samesite="None",
                secure=True,
            )
            response.set_cookie(
                "cart",
                context["cart"],
                max_age=2629800,
                samesite="None",
                secure=True,
            )
            response.set_cookie(
                "order",
                context["order"],
                max_age=2629800,
                samesite="None",
                secure=True,
            )

            return response
    else:
        # post_data_bx_id = '{"ID":"1"}'
        post_data_bx_id = request.COOKIES.get('bitrix_id_order')
        if post_data_bx_id:
            next_url, context, error = get_info_for_order_bitrix(post_data_bx_id, request)
            print(next_url, context, error)
            if error:
                print("ERR")
                return render(request, "admin_specification/error.html", context)
            else:
                if context["type_save"] == "new" or context["spes"] == None:
                    response = HttpResponseRedirect(
                        "/admin_specification/current_specification/"
                    )
                    
                    response.set_cookie(
                        "type_save",
                        "new",
                        max_age=2629800,
                        samesite="None",
                        secure=True,
                    )
                else:
                    response = render(
                        request,
                        next_url,
                        context={
                            "cart": context["cart"],
                            "spes": context["spes"],
                            "serializer": context["serializer"],
                            "type_save": context["type_save"],
                        },
                    )
                print(11111)
                response.set_cookie(
                    "bitrix_id_order",
                    post_data_bx_id,
                    max_age=2629800,
                    samesite="None",
                    secure=True,
                )
                response.set_cookie(
                    "cart",
                    context["cart"],
                    max_age=2629800,
                    samesite="None",
                    secure=True,
                )
                response.set_cookie(
                    "order",
                    context["order"],
                    max_age=2629800,
                    samesite="None",
                    secure=True,
                )

                return response
        else:
            pass



# # Вьюха для редактирования актуальной спецификации и для актуализации недействительной
# @permission_required("specification.add_specification", login_url="/user/login_admin/")
# def update_specification(request):
#     if request.method == "POST":
#         id_specification = json.loads(request.body)
#         current_id = id_specification["specification_id"]

#         products = []

#         current_specification = Specification.objects.filter(pk=current_id)[0]

#         get_products = ProductSpecification.objects.filter(
#             specification=current_specification.pk
#         )

#         for product in get_products:
#             product_id = product.product.pk
#             product_pk = product.pk
#             product_name = product.product.name
#             product_prices = Price.objects.get(prod=product_id)
#             product_price = product_prices.rub_price_supplier
#             product_quantity = product.quantity
#             product_totla_cost = int(product_quantity) * float(product_price)
#             product_id_motrum = product.product.article
#             product_id_suppler = product.product.article_supplier
#             specification_id = current_specification.pk

#             product_individual_sale = product.extra_discount

#             product_price = str(product_price).replace(",", ".")

#             if (
#                 product_individual_sale != "0"
#                 and product_individual_sale != ""
#                 and product_individual_sale != None
#             ):
#                 product_price_extra_old_before = product.price_one / (
#                     1 - float(product_individual_sale) / 100
#                 )

#             else:
#                 product_price_extra_old_before = product.price_one

#             product_price_extra_old = str(product_price_extra_old_before).replace(
#                 ",", "."
#             )
#             product_totla_cost = str(product_totla_cost).replace(",", ".")
#             product_multiplicity_item = Stock.objects.get(prod=product_id)
#             if product_multiplicity_item.is_one_sale == True:
#                 product_multiplicity = 1
#             else:
#                 product_multiplicity = Stock.objects.get(
#                     prod=product_id
#                 ).order_multiplicity
#             discount_item = get_price_motrum(
#                 product.product.category_supplier,
#                 product.product.group_supplier,
#                 product.product.vendor,
#                 product_prices.rub_price_supplier,
#                 product.product.category_supplier_all,
#                 product.product.supplier,
#             )[1]
#             if discount_item == None:
#                 discount = None
#             else:
#                 discount = discount_item.percent

#             data_old = current_specification.date.strftime("%m.%d.%Y")

#             product_item = {
#                 "discount": discount,
#                 "id": product_id,
#                 "idMotrum": product_id_motrum,
#                 "idSaler": product_id_suppler,
#                 "name": product_name,
#                 "price": product_price,
#                 "quantity": product_quantity,
#                 "totalCost": product_totla_cost,
#                 "productSpecificationId": product_pk,
#                 "specificationId": specification_id,
#                 "multiplicity": product_multiplicity,
#                 "product_price_extra_old": product_price_extra_old,
#                 "data_old": data_old,
#                 "product_individual_sale": product_individual_sale,
#             }

#             products.append(product_item)

#     current_products = json.dumps(products)

#     out = {
#         "status": "ok",
#         "products": current_products,
#     }
#     return JsonResponse(out)

# def load_products(request):
#     data = json.loads(request.body)
#     cat = data["category"]
#     gr = data["group"]
#     page_num = data["pageNum"]

#     if page_num == "":
#         start_point = 9
#     else:
#         start_point = int(page_num) * 9

#     endpoint_product = start_point + 9

#     if gr == "" and cat == "":
#         product_list = (
#             Product.objects.prefetch_related(
#                 "supplier",
#                 "vendor",
#                 "category_supplier_all",
#                 "group_supplier",
#                 "category_supplier",
#                 "category",
#                 "group",
#                 "price",
#                 "stock",
#             )
#             .all()
#             .order_by("pk")
#         )
#     elif gr == "":
#         product_list = (
#             Product.objects.prefetch_related(
#                 "supplier",
#                 "vendor",
#                 "category_supplier_all",
#                 "group_supplier",
#                 "category_supplier",
#                 "category",
#                 "group",
#                 "price",
#                 "stock",
#             )
#             .filter(category=cat)
#             .order_by("pk")
#         )
#     else:
#         product_list = (
#             Product.objects.select_related(
#                 "supplier",
#                 "vendor",
#                 "category",
#                 "group",
#             )
#             .filter(category=cat, group=gr)
#             .order_by("pk")
#         )

#     items = product_list[start_point:endpoint_product]

#     products = []

#     for product_elem in items:


#         try:
#             price_all = Price.objects.get(prod=product_elem.pk)
#             price = price_all.rub_price_supplier
#             price_suppler = price_all.price_motrum

#             discount = get_price_motrum(
#             product_elem.category_supplier,
#             product_elem.group_supplier,
#             product_elem.vendor,
#             price,
#             product_elem.category_supplier_all,
#         )[1].percent
#         except Price.DoesNotExist:
#             price_all = None
#             price = None
#             price_suppler = 0
#             discount = None

#         chars = ProductProperty.objects.filter(product=product_elem.pk)
#         try:
#             stock_item =  Stock.objects.get(prod=product_elem.pk)
#             lotname = stock_item.lot.name_shorts

#             if stock_item.is_one_sale == True:
#                 product_multiplicity = 1
#             else:
#                 product_multiplicity = Stock.objects.get(
#                     prod=product_elem.pk
#                 ).order_multiplicity

#         except:
#             stock_item =  None
#             lotname = None
#             product_multiplicity = 1


#         name = product_elem.name
#         pk = product_elem.pk
#         article = product_elem.article
#         saler_article = product_elem.article_supplier


#         characteristics = []
#         for char in chars:
#             characteristics.append(char.value)


#         product = {
#             "name": name,
#             "lot": lotname,
#             "pk": pk,
#             "article": article,
#             "saler_article": saler_article,
#             "price": price,
#             "chars": characteristics,
#             "price_suppler": price_suppler,
#             "discount": discount,
#             "multiplicity": product_multiplicity,
#         }
#         products.append(product)

#     current_products = json.dumps(products)
#     out = {"status": "ok", "products": current_products}
#     return JsonResponse(out, safe=False)


# def update_specification(request):
#     if request.method == "POST":
#         id_specification = json.loads(request.body)
#         current_id = id_specification["specification_id"]

#         products = []

#         current_specification = Specification.objects.filter(pk=current_id)[0]

#         get_products = ProductSpecification.objects.filter(
#             specification=current_specification.pk
#         )

#         for product in get_products:
#             product_id = product.product.pk
#             product_pk = product.pk
#             product_name = product.product.name
#             product_prices = Price.objects.get(prod=product_id)
#             product_price = product_prices.rub_price_supplier
#             product_quantity = product.quantity
#             product_totla_cost = int(product_quantity) * float(product_price)
#             product_id_motrum = product.product.article
#             product_id_suppler = product.product.article_supplier

#             # suppelier = Product.objects.filter(pk=product_id)[0].supplier
#             # discount = Discount.objects.filter(supplier=suppelier)[0].percent
#             specification_id = current_specification.pk

#             product_price = str(product_price).replace(",", ".")
#             product_totla_cost = str(product_totla_cost).replace(",", ".")
#             product_multiplicity_item = Stock.objects.get(prod=product_id)
#             if product_multiplicity_item.is_one_sale == True:
#                 product_multiplicity = 1
#             else:
#                 product_multiplicity = Stock.objects.get(
#                     prod=product_id
#                 ).order_multiplicity
#             discount = get_price_motrum(
#                 product.product.category_supplier,
#                 product.product.group_supplier,
#                 product.product.vendor,
#                 product_prices.rub_price_supplier,
#                 product.product.category_supplier_all,
#             )[1].percent

#             product_item = {
#                 "discount": discount,
#                 "id": product_id,
#                 "idMotrum": product_id_motrum,
#                 "idSaler": product_id_suppler,
#                 "name": product_name,
#                 "price": product_price,
#                 "quantity": product_quantity,
#                 "totalCost": product_totla_cost,
#                 "productSpecificationId": product_pk,
#                 "specificationId": specification_id,
#                 "multiplicity": product_multiplicity,
#             }

#             products.append(product_item)

#     current_products = json.dumps(products)

#     out = {
#         "status": "ok",
#         "products": current_products,
#     }
#     return JsonResponse(out)


# рендер страницы корзины до переверстки
# @permission_required("specification.add_specification", login_url="/user/login_admin/")
# def create_specification(request):
#     cart = request.COOKIES.get("cart")
#     # если есть корзина
#     if cart != None:

#         cart_qs = Cart.objects.get(id=cart)
#         discount_client = 0
#         if cart_qs.client:
#             discount_client = Client.objects.filter(id=cart_qs.client.id)

#         product_cart_list = ProductCart.objects.filter(cart=cart).values_list(
#             "product__id"
#         )

#         product_cart = ProductCart.objects.filter(cart=cart)
#         # изменение спецификации
#         try:
#             specification = Specification.objects.get(cart=cart)

#             product_specification = ProductSpecification.objects.filter(
#                 specification=specification
#             )
#             mortum_req = BaseInfo.objects.all().prefetch_related(
#                 Prefetch("BaseInfoAccountRequisites"),

#             )
#         # новая спецификация
#         except Specification.DoesNotExist:
#             specification = None
#             product_specification = ProductSpecification.objects.filter(
#                 specification=specification
#             )
#             mortum_req = BaseInfoAccountRequisites.objects.all().select_related("requisites")

#         prefetch_queryset_property = ProductProperty.objects.filter(
#             product__in=product_cart_list
#         )

#         # продукты которые есть в окт в корзине
#         product = (
#             Product.objects.filter(id__in=product_cart_list)
#             .select_related(
#                 "supplier",
#                 "vendor",
#                 "category",
#                 "group",
#                 "price",
#                 "stock",
#                 "category_supplier_all",
#                 "group_supplier",
#                 "category_supplier",
#                 # "stock__lot",
#             )
#             .prefetch_related(
#                 Prefetch("stock__lot"),
#                 Prefetch("productproperty_set"),
#                 Prefetch("price__sale"),
#             )
#             .annotate(
#                 quantity=product_cart.filter(product=OuterRef("pk")).values(
#                     "quantity",
#                 ),
#                 id_product_cart=product_cart.filter(product=OuterRef("pk")).values(
#                     "id",
#                 ),
#                 id_product_spesif=product_specification.filter(
#                     product=OuterRef("pk")
#                 ).values(
#                     "id",
#                 ),
#                 comment=product_specification.filter(
#                     product=OuterRef("pk")
#                 ).values(
#                     "comment",
#                 ),
#             )
#         )

#         id_specification = request.COOKIES.get("specificationId")
#         if id_specification:
#             # product_new = ProductCart.objects.filter(cart=cart,product=None,)
#             product_new = ProductSpecification.objects.filter(
#                 specification=specification,
#                 product=None,
#             ).annotate(
#                 id_product_cart=product_cart.filter(
#                     product_new=OuterRef("product_new")
#                 ).values(
#                     "id",
#                 ),
#             )
#             product_new_value_id = product_new.values_list("id_product_cart")
#             product_new_more = ProductCart.objects.filter(
#                 cart=cart, product=None
#             ).exclude(id__in=product_new_value_id)
#             update_spesif = True

#         else:
#             product_new = ProductCart.objects.filter(cart=cart, product=None)
#             product_new_more = None
#             update_spesif = False

#         if id_specification:
#             title = f"Cпецификация № {id_specification}"
#         else:
#             title = "Новая спецификация"


#     # корзины нет
#     else:
#         mortum_req = None
#         title = "Новая спецификация"
#         product = None
#         product_new = None
#         cart = None
#         update_spesif = False
#         product_new_more = None
#         specification = None
#         order = None

#     current_date = datetime.date.today().isoformat()

#     context = {
#         "title": title,
#         "product": product,
#         "product_new": product_new,
#         "cart": cart,
#         "request": request,
#         "current_date": current_date,
#         "update_spesif": update_spesif,
#         "product_new_more": product_new_more,
#         "specification" : specification,
#         "mortum_req":mortum_req,
#         "order":order
#     }
#     return render(request, "admin_specification/catalog.html", context)
