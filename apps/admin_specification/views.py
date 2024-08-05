import json
import os
from click import group
from django.core import serializers
from django.db.models import Prefetch

from django.http import JsonResponse
from django.shortcuts import render
from apps.core.utils import get_price_motrum, save_specification
from apps.product.models import (
    CategoryProduct,
    GroupProduct,
    Lot,
    Price,
    Product,
    ProductProperty,
    Stock,
)
from django.core.paginator import Paginator
from django.contrib.auth.decorators import permission_required, login_required
from django.utils.decorators import method_decorator
from apps.specification.models import ProductSpecification, Specification
from apps.specification.utils import crete_pdf_specification
from apps.supplier.models import Discount
from apps.user.models import AdminUser
from project.settings import MEDIA_ROOT
from .forms import SearchForm
from django.db.models import Q


# Рендер главной страницы каталога с пагинацией
@permission_required('specification.add_specification',login_url='/user/login_admin/')
def all_categories(request):
    title = "Каталог"
    categories = CategoryProduct.objects.all().order_by("article_name")

    product_list = Product.objects.select_related(
        "supplier",
        "vendor",
        "category_supplier_all",
        "group_supplier",
        "category_supplier",
        "category",
        "group",
        "price",
        "stock",
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
    }
    
    renders =  "admin_specification/categories.html"

    
    return render(request, "admin_specification/categories.html", context)


# Рендер страницы групп товаров с пагинацией
@permission_required('specification.add_specification',login_url='/user/login_admin/')
def group_product(request, cat):
    categoryes = CategoryProduct.objects.all().order_by("article_name")
    groups = GroupProduct.objects.select_related("category").filter(category=cat).order_by("article_name")
    product_list = Product.objects.select_related(
        "supplier",
        "vendor",
        "category_supplier_all",
        "group_supplier",
        "category_supplier",
        "category",
        "group",
        "price",
        "stock",
    ).filter(category=cat)

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
    }

    return render(request, "admin_specification/group.html", context)


# Рендер страницы подгрупп с пагинацией
@permission_required('specification.add_specification',login_url='/user/login_admin/')
def specifications(request, cat, gr):
    categoryes = CategoryProduct.objects.all().order_by("article_name")
    product_list = Product.objects.select_related(
        "supplier",
        "vendor",
        "category_supplier_all",
        "group_supplier",
        "category_supplier",
        "category",
        "group",
        "price",
        "stock",
    ).filter(category=cat, group=gr)

    groups = GroupProduct.objects.select_related("category").all().order_by("article_name")

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
    }
    return render(request, "admin_specification/specification_page.html", context)


# рендер страницы корзины
@permission_required('specification.add_specification',login_url='/user/login_admin/')
def create_specification(request):
    cookie = request.COOKIES.get("key")
    if cookie:
        key = json.loads(cookie)
    else:
        key = []
        
    id_specification =  request.COOKIES.get("specificationId") 
    
    if id_specification:
        title = f"Cпецификация № {id_specification}"
    else:
         title = "Текущая спецификация"
        
   
    
    context = {
        "title": title,
        "specification_items": key,
    }
    return render(request, "admin_specification/catalog.html", context)


# Вьюха для сохранения спецификации
@permission_required('specification.add_specification',login_url='/user/login_admin/')
def save_specification_view_admin(request):
    from apps.specification.models import ProductSpecification, Specification

    received_data = json.loads(request.body)

    # сохранение спецификации
    save_specification(received_data)

    out = {"status": "ok", "data": received_data}
    return JsonResponse(out)


# рендер страницы со всеми спецификациями
@permission_required('specification.add_specification',login_url='/user/login_admin/',)
def get_all_specifications(request):

    all_specifications = (
        Specification.objects.select_related(
            "admin_creator",
        )
        .all()
        .order_by("pk")
        .reverse()
    )
    print( AdminUser.user)
    user_admin = AdminUser.objects.get(user=request.user)
    user_admin_type = user_admin.admin_type
    
    if user_admin_type == "ALL":
        pass
    elif user_admin_type == "BASE":
        all_specifications = all_specifications.filter(admin_creator_id= request.user.id)


    media_root = os.path.join(MEDIA_ROOT, "")

    title = "Все спецификации"
    context = {
        "title": title,
        "specifications": all_specifications,
        "media_root": media_root,
    }
  
    return render(request, "admin_specification/all_specifications.html", context)


# рендер страницы товаров у которых есть категория, но нет групп
@permission_required('specification.add_specification',login_url='/user/login_admin/')
def instruments(request, cat):

    category = CategoryProduct.objects.filter(pk=cat).order_by("article_name")
    product_list = Product.objects.select_related(
        "supplier",
        "vendor",
        "category_supplier_all",
        "group_supplier",
        "category_supplier",
        "category",
        "group",
        "price",
        "stock",
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
    }

    return render(request, "admin_specification/specification_page.html", context)


# Вьюха для аякс поиска, подзагрузка товаров при скролле вниз
@permission_required('specification.add_specification',login_url='/user/login_admin/')
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
        ).all()
    elif gr == "":
        product_list = Product.objects.select_related(
            "supplier",
            "vendor",
            "category",
            "group",
        ).filter(category=cat)
    else:
        product_list = Product.objects.select_related(
            "supplier",
            "vendor",
            "category",
            "group",
        ).filter(category=cat, group=gr)
  
    product_list = product_list.filter(
        Q(name__icontains=value)
        | Q(article__icontains=value)
        | Q(article_supplier__icontains=value)
        | Q(additional_article_supplier__icontains=value)
    )
    items = product_list[start:counter]

    products = serializers.serialize("json", items)
    out = {"status": "ok", "products": products}
    return JsonResponse(out)


# Вьюха логики при нажатии на кнопку "Загрузить ещё"
@permission_required('specification.add_specification',login_url='/user/login_admin/')
def load_products(request):
    data = json.loads(request.body)
    cat = data["category"]
    gr = data["group"]
    page_num = data["pageNum"]
    print(1111111111)
    print(data)
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
                "category_supplier_all",
                "group_supplier",
                "category_supplier",
                "category",
                "group",
                "price",
                "stock",
            )
            .all()
            .order_by("pk")
        )
    elif gr == "":
        product_list = (
            Product.objects.prefetch_related(
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
            .filter(category=cat)
            .order_by("pk")
        )
    else:
        product_list = (
            Product.objects.select_related(
                "supplier",
                "vendor",
                "category",
                "group",
            )
            .filter(category=cat, group=gr)
            .order_by("pk")
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
                product.product.supplier,
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
        article = product_elem.article
        saler_article = product_elem.article_supplier

        characteristics = []
        for char in chars:
            characteristics.append(char.value)

        product = {
            "name": name,
            "lot": lotname,
            "pk": pk,
            "article": article,
            "saler_article": saler_article,
            "price": price,
            "chars": characteristics,
            "price_suppler": price_suppler,
            "discount": discount,
            "multiplicity": product_multiplicity,
        }
        products.append(product)

    current_products = json.dumps(products)
    out = {"status": "ok", "products": current_products}
    return JsonResponse(out, safe=False)


# Вьюха для редактирования актуальной спецификации и для актуализации недействительной
@permission_required('specification.add_specification',login_url='/user/login_admin/')
def update_specification(request):
    if request.method == "POST":
        id_specification = json.loads(request.body)
        current_id = id_specification["specification_id"]

        products = []

        current_specification = Specification.objects.filter(pk=current_id)[0]

        get_products = ProductSpecification.objects.filter(
            specification=current_specification.pk
        )

        for product in get_products:
            product_id = product.product.pk
            product_pk = product.pk
            product_name = product.product.name
            product_prices = Price.objects.get(prod=product_id)
            product_price = product_prices.rub_price_supplier
            product_quantity = product.quantity
            product_totla_cost = int(product_quantity) * float(product_price)
            product_id_motrum = product.product.article
            product_id_suppler = product.product.article_supplier
            specification_id = current_specification.pk
            
            product_individual_sale = product.extra_discount
            
            product_price = str(product_price).replace(",", ".")
            
            if product_individual_sale != '0' and product_individual_sale != '' and product_individual_sale != None:
                product_price_extra_old_before = product.price_one / (1 - float(product_individual_sale) /
                    100)
                print(product_price_extra_old_before)
            else: 
                product_price_extra_old_before = product.price_one
           
            product_price_extra_old = str(product_price_extra_old_before).replace(",", ".")
            product_totla_cost = str(product_totla_cost).replace(",", ".")
            product_multiplicity_item = Stock.objects.get(prod=product_id)
            if product_multiplicity_item.is_one_sale == True:
                product_multiplicity = 1
            else:
                product_multiplicity = Stock.objects.get(
                    prod=product_id
                ).order_multiplicity
            discount_item = get_price_motrum(
                product.product.category_supplier,
                product.product.group_supplier,
                product.product.vendor,
                product_prices.rub_price_supplier,
                product.product.category_supplier_all,
                product.product.supplier,
            )[1]
            if discount_item == None:
                discount = None
            else:
                discount = discount_item.percent
                
            data_old = current_specification.date.strftime("%m.%d.%Y")
           

            product_item = {
                "discount": discount,
                "id": product_id,
                "idMotrum": product_id_motrum,
                "idSaler": product_id_suppler,
                "name": product_name,
                "price": product_price,
                "quantity": product_quantity,
                "totalCost": product_totla_cost,
                "productSpecificationId": product_pk,
                "specificationId": specification_id,
                "multiplicity": product_multiplicity,
                "product_price_extra_old":product_price_extra_old,
                "data_old":data_old,
                "product_individual_sale":product_individual_sale
            }

            products.append(product_item)

    current_products = json.dumps(products)

    out = {
        "status": "ok",
        "products": current_products,
        
    }
    return JsonResponse(out)


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
