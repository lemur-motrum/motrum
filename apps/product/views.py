import os
import re
from collections import defaultdict
from django.shortcuts import redirect, render
from dal import autocomplete
from django.db.models import Q
from dal_select2.views import Select2ViewMixin
from dal.views import BaseQuerySetView
from regex import P
from django.db.models import Prefetch
from apps import product
from apps.admin_specification.views import all_categories
from apps.core.utils import get_file_path_add_more_doc, get_props_all_motrum_filter, get_props_all_motrum_filter3, get_props_motrum_filter, get_props_motrum_filter_to_view, serch_products_web
from apps.product.forms import DocumentForm
from apps.product.models import (
    TYPE_DOCUMENT,
    CategoryProduct,
    GroupProduct,
    Product,
    ProductDocument,
    ProductImage,
    ProductProperty,
    ProductPropertyMotrum,
    ProductPropertyMotrumItem,
    ProductPropertyValueMotrum,
    Stock,
    VendorPropertyAndMotrum,
)
from apps.supplier.models import (
    SupplierCategoryProduct,
    SupplierCategoryProductAll,
    SupplierGroupProduct,
    Vendor,
)
from apps.user import forms
from project.settings import MEDIA_ROOT, MEDIA_URL


# все категории
def catalog_all(request):
    print("catalog_all")
    # category = CategoryProduct.objects.all().order_by("article_name")
    category = (
        CategoryProduct.objects.prefetch_related(
            Prefetch("product_set"),
        )
        .filter()
        .exclude(product__isnull=True)
        .order_by("article_name")
    )

    vendors = Vendor.objects.filter(is_view_index_web=True)[0:4]

    context = {
        "category": category,
        "title": "Товары",
        "vendors": vendors,
        "meta_title": "Товары | Мотрум - автоматизация производства",
    }

    return render(request, "product/product_catalog.html", context)


# группы категорий
def catalog_group(request, category):
    print("catalog_group")
    media_url = MEDIA_URL
    search_text = None

    group = (
        GroupProduct.objects.filter(category__slug=category)
        .prefetch_related(
            Prefetch("product_set"),
        )
        .exclude(product__isnull=True)
        .order_by("article_name")
    )

    # товарфы в группе
    if len(group) > 0 and category != "search":
        cat = CategoryProduct.objects.get(slug=category)
        all_categories = (
            CategoryProduct.objects.prefetch_related(
                Prefetch("product_set"),
            )
            .filter()
            .exclude(
                product__isnull=True,
            )
            .exclude(pk=cat.pk)
            .order_by("article_name")
        )

        def get_another_category():
            current_cats = [
                category for category in all_categories if category.pk != cat.pk
            ]
            return current_cats

        context = {
            "category": cat,
            "group": group,
            # "another_categories": get_another_category(),
            "another_categories": all_categories,
            "title": cat.name,
            "meta_title": f"{cat.name}| Мотрум - автоматизация производства",
        }

        return render(request, "product/product_group.html", context)
    # все твоары в категории или все твоары .товары без категории. товары поиска
    else:

        q_object = Q()
        q_object &= Q(check_to_order=True, in_view_website=True)

        if category is not None:
            if category == "other":
                q_object &= Q(category=None)
            elif category == "all":
                q_object &= Q(article__isnull=False)
            elif category == "search":
                search_text = request.GET.get("search_text")
                q_object &= Q(article__isnull=False)

            else:
                q_object &= Q(category__slug=category)

        queryset = Product.objects.select_related(
            "vendor",
            "category",
        ).filter(q_object)

        if search_text and search_text != "":

            queryset = serch_products_web(search_text, queryset)

        
        product_vendor = (
            queryset.order_by("vendor__name")
            .distinct("vendor__name")
            .values("vendor", "vendor__name", "vendor__slug", "vendor__img")
        )
        product_props_motrum = ProductPropertyMotrumItem.objects.filter(product__in=queryset
        )
        chars_motrum = get_props_motrum_filter_to_view(product_props_motrum)

        try:
            current_category = CategoryProduct.objects.get(slug=category)
        except:
            if category == "all":
                current_category = {
                    "meta_title": f"Все товары | Мотрум - автоматизация производства",
                    "name": "Все товары",
                    "slug": category,
                }
            elif category == "other":
                current_category = {
                    "meta_title": f"Товары без категории| Мотрум - автоматизация производства",
                    "name": "Товары без категории",
                    "slug": category,
                }
            elif category == "search":
                search_text = request.GET.get("search_text")
                name = f"Поиск: {search_text}"
                current_category = {
                    "meta_title": f"Поиск по товарам |Мотрум - автоматизация производства",
                    "name": name,
                    "slug": category,
                }
            else:
                current_category = {
                    "meta_title": f"Мотрум - автоматизация производства",
                    "name": "Все товары",
                    "slug": category,
                }

        context = {
            "current_category": current_category,
            "product_vendor": product_vendor,
            "chars_motrum": chars_motrum,
            "media_url": media_url,
        }
        return render(request, "product/catalog.html", context)


# страница всех продуктов в категории\группе + фильтры
def products_items(request, category, group):
    print("products_items")
    media_url = MEDIA_URL
    q_object = Q()
    q_object &= Q(check_to_order=True, in_view_website=True)
    if category is not None:
        q_object &= Q(category__slug=category)
    if group is not None:
        q_object &= Q(group__slug=group)

    product = Product.objects.select_related(
        "vendor",
        "category",
        "group",
    ).filter(q_object)

    

    product_vendor = (
        product.order_by("vendor__name")
        .distinct("vendor__name")
        .values("vendor", "vendor__name", "vendor__slug", "vendor__img")
    )
    
    
    product_props_motrum = ProductPropertyMotrumItem.objects.filter( product__in=product
        )
    chars_motrum = get_props_motrum_filter_to_view(product_props_motrum)
    
    
    current_category = CategoryProduct.objects.get(slug=category)
    current_group = GroupProduct.objects.get(slug=group)

    another_groups = (
        GroupProduct.objects.filter(category__slug=category)
        .prefetch_related(
            Prefetch("product_set"),
        )
        .exclude(product__isnull=True)
        .exclude(pk=current_group.pk)
        .order_by("article_name")
    )

    

    context = {
        "current_category": current_category,
        "current_group": current_group,
        "product_vendor": product_vendor,
    
        "another_groups": another_groups,
        "title": current_group.name,
        "media_url": media_url,
       
        "chars_motrum": chars_motrum,
        "meta_title": f"{current_group.name} | Мотрум - автоматизация производства",
    }

    return render(request, "product/catalog.html", context)


# страница отдельного продукта
def product_one(request, category, group, article):
    print("product_one")
    product = Product.objects.get(article=article)
    product = (
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
            Prefetch("productimage_set"),
            Prefetch("productdocument_set"),
        )
        .get(article=article)
    )

    product_document = ProductDocument.objects.filter(product=product, hide=False)

    id_ex = []
    for product_docum in product_document:
        dir_img = "{0}/{1}".format(MEDIA_ROOT, product_docum.document)
        if not os.path.exists(dir_img):
            id_ex.append(product_docum.id)

    product_document = product_document.exclude(id__in=id_ex)

    context = {
        "product": product,
        "current_category": product.category,
        "current_group": product.group,
        "title": product.name,
        "product_document": product_document,
        "meta_title": f"{product.name} | Мотрум - автоматизация производства",
    }
    return render(request, "product/product_one.html", context)


# страница отдельного продукта без с категорией но без группы
def product_one_without_group(request, category, article):
    if category == "other":
        current_category = {
            "name": "Товары без категории",
            "slug": category,
        }
    # else:
    #     current_category = {
    #         "name": "Товары без категории",
    #         "slug": category,
    #     }
    else:
        current_category = CategoryProduct.objects.get(slug=category)

    product = (
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
            Prefetch("productimage_set"),
        )
        .get(article=article)
    )
    product_document = ProductDocument.objects.filter(product=product, hide=False)
    id_ex = []
    for product_docum in product_document:
        dir_img = "{0}/{1}".format(MEDIA_ROOT, product_docum.document)
        if not os.path.exists(dir_img):
            id_ex.append(product_docum.id)

    product_document = product_document.exclude(id__in=id_ex)
  

    context = {
        "product": product,
        "current_category": current_category,
        "title": product.name,
        "product_document": product_document,
        "meta_title": f"{product.name} | Мотрум - автоматизация производства",
       
    }
    return render(request, "product/product_one.html", context)


def product_search(request):
    pass


# страница брендов общая
def brand_all(request):

    brands = (
        Vendor.objects.filter(product__isnull=False, product__in_view_website=True)
        .distinct()
        .order_by("article", "name")
    )

    context = {
        "brands": brands,
        "meta_title": "Продукты | Мотрум - автоматизация производства",
    }

    return render(request, "product/brand_all.html", context)


# страница бренда одного с товарами
def brand_one(request, vendor):
    print("page brand_one")
    brand = Vendor.objects.get(slug=vendor)
    product = Product.objects.select_related(
        "vendor",
        "category",
        "group",
    ).filter(vendor=brand)
    
    product_props_motrum = ProductPropertyMotrumItem.objects.filter(product__in=product
        )
    chars_motrum = get_props_motrum_filter_to_view(product_props_motrum)
    
    context = {
        "brand": brand,
        "chars_motrum": chars_motrum,
        "meta_title": f"{brand.name} | Мотрум - автоматизация производства",
    }
    return render(request, "product/brand_one.html", context)


def add_document_admin(request):
    from pytils import translit
    from django.core.files import File

    id_selected = request.GET.get("context")
    id_selected = list(
        map(int, id_selected[1:-1].split(", "))
    )  # No need for list call in Py2
    form = DocumentForm()
    from django.core.files.storage import FileSystemStorage

    if request.method == "POST":
        file_path = None

        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():

            profile = form.save(commit=False)
            file_name = request.FILES["document"].name

            type_doc = request.POST["type_doc"]
            name_doc = request.POST["name"]

            images_last_list = file_name.split(".")
            type_file = "." + images_last_list[-1]

            new_dir, link, slugish = get_file_path_add_more_doc(
                product, profile.type_doc, profile.name
            )

            in_memory_file_obj = request.FILES["document"]
            # f = FileSystemStorage(location=new_dir).save(
            #     in_memory_file_obj.name, in_memory_file_obj
            # )
            doc_name = f"{slugish}{type_file}"
            f = FileSystemStorage(location=new_dir).save(doc_name, in_memory_file_obj)

            for id_prod in id_selected:
                doc = f"{link}/{f}"
                product_doc = ProductDocument.objects.create(
                    product_id=int(id_prod),
                    type_doc=type_doc,
                    name=name_doc,
                    document=doc,
                )

                # for chunk in request.FILES["document"].chunks():
                #     dest.write(chunk)

                # with open(f"{name[0]}{type_file}", "wb+") as destination:
                #     for chunk in request.FILES["document"].chunks():
                #         destination.write(chunk)
                # ProductDocument.image.save("image.jpg", File(img_temp), save=True)

                # if file_path:
                #     document = ProductDocument.objects.create(product=product,document = file_path,type_doc=profile.type_doc,name=profile.name, )

                #     # document.document.field.upload_to = get_file_path_add_more_doc(product,profile.type_doc,request.FILES["document"],file_path)

                # else:
                #     profile.product = product
                #     profile.save()
                #     file_path = profile.document

                # else:
                #     print(form.errors)
            context = {"type_document": TYPE_DOCUMENT, "form": form, "create": "ok"}
        return render(request, "admin/add_doc.html", context)
    else:
        form = DocumentForm()
        context = {"type_document": TYPE_DOCUMENT, "form": form, "create": None}
        return render(request, "admin/add_doc.html", context)


# АВТОЗАПОЛНЕНИЯ для админки БЕК ОКТ
class VendorAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Vendor.objects.all()
        supplier = self.forwarded.get("supplier", None)

        if supplier:
            qs = qs.filter(supplier=supplier)

        vendor = self.forwarded.get("vendor", None)
        if vendor:
            qs = qs.filter(vendor=vendor)

        if self.q:
            qs = qs.filter(Q(name__icontains=self.q))

        return qs


class GropeAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = GroupProduct.objects.all()

        category = self.forwarded.get("category", None)

        if category:
            qs = qs.filter(category=category)

        group = self.forwarded.get("group", None)
        if group:
            qs = qs.filter(group=group)

        if self.q:
            # name__icontains=self.q
            qs = qs.filter(Q(name__icontains=self.q))

        return qs


class SupplierCategoryProductAllAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = SupplierCategoryProductAll.objects.all()

        # supplier = self.forwarded.get("supplier", None)
        # if supplier:
        #     qs = qs.filter(supplier=supplier)

        vendor = self.forwarded.get("vendor", None)
        if vendor:
            qs = qs.filter(vendor=vendor)

        category_supplier = self.forwarded.get("category_supplier", None)
        if category_supplier:
            qs = qs.filter(category_supplier=category_supplier)

        group_supplier = self.forwarded.get("group_supplier", None)
        if group_supplier:
            qs = qs.filter(group_supplier=group_supplier)

        if self.q:
            # name__icontains=self.q
            qs = qs.filter(Q(name__icontains=self.q))

        return qs


class SupplierCategoryProductAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = SupplierCategoryProduct.objects.all()
        supplier = self.forwarded.get("supplier", None)
        vendor = self.forwarded.get("vendor", None)

        supplier = self.forwarded.get("supplier", None)
        if supplier:
            qs = qs.filter(supplier=supplier)

        # vendor = self.forwarded.get("vendor", None)
        # if vendor:
        #     qs = qs.filter(vendor=vendor)

        # if supplier and vendor:
        #     qs = qs.filter(supplier=supplier,vendor=vendor)
        #     if qs.count() == 0:
        #         qs = SupplierCategoryProduct.objects.filter(supplier=supplier)

        if self.q:
            # name__icontains=self.q
            qs = qs.filter(Q(name__icontains=self.q))
        return qs


class SupplierGroupProductAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = SupplierGroupProduct.objects.all()
        category_supplier = self.forwarded.get("category_supplier", None)
        if category_supplier:
            qs = qs.filter(category_supplier=category_supplier)

        if self.q:
            # name__icontains=self.q
            qs = qs.filter(Q(name__icontains=self.q))
        return qs
    
    
class ProductPropertyValueMotrumAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = ProductPropertyValueMotrum.objects.all()
        property_motrum = self.forwarded.get("property_motrum", None)
        if property_motrum:
            qs = qs.filter(property_motrum=property_motrum)

        if self.q:
            # name__icontains=self.q
            qs = qs.filter(Q(value__icontains=self.q))
        return qs


class ProductPropertyMotrumAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = ProductPropertyMotrum.objects.all()
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs
