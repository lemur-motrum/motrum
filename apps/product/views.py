import os
import re
from django.shortcuts import redirect, render
from dal import autocomplete
from django.db.models import Q
from dal_select2.views import Select2ViewMixin
from dal.views import BaseQuerySetView
from regex import P
from django.db.models import Prefetch
from apps import product
from apps.admin_specification.views import all_categories
from apps.core.utils import get_file_path_add_more_doc
from apps.product.forms import DocumentForm
from apps.product.models import (
    TYPE_DOCUMENT,
    CategoryProduct,
    GroupProduct,
    Product,
    ProductDocument,
    ProductProperty,
    Stock,
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
    category = CategoryProduct.objects.all().order_by("article_name")
    vendors = Vendor.objects.filter(is_view_index_web=True)

    print(category)

    context = {
        "category": category,
        "title": "Товары",
        "vendors": vendors,
    }

    return render(request, "product/product_catalog.html", context)


# группы категорий
def catalog_group(request, category):
    print("catalog_group")
    media_url = MEDIA_URL
    group = GroupProduct.objects.filter(category__slug=category).order_by(
        "article_name"
    )

    if len(group) > 0:
        all_categories = CategoryProduct.objects.all()
        cat = CategoryProduct.objects.get(slug=category)

        def get_another_category():
            current_cats = [
                category for category in all_categories if category.pk != cat.pk
            ]
            return current_cats

        context = {
            "category": cat,
            "group": group,
            "another_categories": get_another_category(),
            "title": cat.name,
        }

        return render(request, "product/product_group.html", context)
    else:
        # vendor = Vendor.objects.filter()
        q_object = Q()
        q_object &= Q(check_to_order=True, in_view_website=True)
        print(q_object)
        if category is not None:
            # q_object &= Q(category__slug=category)
            if category == "other":
                q_object &= Q(category=None)
            elif category == "all":
                q_object &= Q(article__isnull=False)
            else:
                q_object &= Q(category__slug=category)

        product_vendor = (
            Product.objects.select_related(
                "vendor",
                "category",
            )
            .filter(q_object)
            .order_by("vendor__name")
            .distinct("vendor__name")
            .values("vendor", "vendor__name", "vendor__slug", "vendor__img")
        )
        print(product_vendor)
        try:
            current_category = CategoryProduct.objects.get(slug=category)
        except:
            if category == "all":
                current_category = {"name": "Все товары", "slug": category}
            elif category == "other":
                current_category = {
                    "name": "Товары без категории",
                    "slug": category,
                }

        context = {
            "current_category": current_category,
            "product_vendor": product_vendor,
            "media_url": media_url,
        }
        return render(request, "product/catalog.html", context)


# страница всех продуктов в категории\группе
def products_items(request, category, group):
    print("products_items")
    media_url = MEDIA_URL
    q_object = Q()
    q_object &= Q(check_to_order=True, in_view_website=True)
    if category is not None:
        q_object &= Q(category__slug=category)
    if group is not None:
        q_object &= Q(group__slug=group)

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
    current_category = CategoryProduct.objects.get(slug=category)
    current_group = GroupProduct.objects.get(slug=group)

    all_groups = (
        GroupProduct.objects.select_related("category").all().order_by("article_name")
    )

    def get_another_groups():
        current_groups = [
            group_elem
            for group_elem in all_groups
            if group_elem.pk != current_group.pk
            and group_elem.category.pk == current_category.pk
        ]
        return current_groups

    context = {
        "current_category": current_category,
        "current_group": current_group,
        "product_vendor": product_vendor,
        "another_groups": get_another_groups(),
        "title": current_group.name,
        "media_url": media_url,
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
    product_document = ProductDocument.objects.filter(product=product)

    context = {
        "product": product,
        "current_category": product.category,
        "current_group": product.group,
        "title": product.name,
        "product_document": product_document,
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
    # product = Product.objects.get(article=article)
    # product_properties = ProductProperty.objects.filter(product=product.pk)
    # product_lot = Stock.objects.get(prod=product.pk)

    context = {
        "product": product,
        "current_category": current_category,
        "title": product.name,
        # "product_properties": product_properties,
        # "product_lot": product_lot,
    }
    return render(request, "product/product_one.html", context)


# страница брендов общая
def brand_all(request):
    brands = (
        Vendor.objects.all()
        .order_by("article", "name")
    )
    print(brands)
    context = {
        "brands": brands,
    }

    return render(request, "product/brand_all.html", context)


# страница бренда одного с товарами
def brand_one(request, vendor):
    brand = Vendor.objects.get(slug=vendor)

    print(brand)
    context = {
        "brand": brand,
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
        for id_select in id_selected:
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                product = Product.objects.get(id=id_select)
                profile = form.save(commit=False)
                file_name = request.FILES["document"].name
                images_last_list = file_name.split(".")
                type_file = "." + images_last_list[-1]

                name = get_file_path_add_more_doc(
                    product, profile.type_doc, profile.name
                )

                in_memory_file_obj = request.FILES["document"]
                FileSystemStorage(location="/").save(
                    in_memory_file_obj.name, in_memory_file_obj
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

            else:
                print(form.errors)
            context = {"type_document": TYPE_DOCUMENT, "form": form, "create": "ok"}
        return render(request, "admin/add_doc.html", context)
    else:
        form = DocumentForm()
        context = {"type_document": TYPE_DOCUMENT, "form": form, "create": None}
        return render(request, "admin/add_doc.html", context)


# # юрина вьюха каталога
# def catalog(request):

#     product_list = Product.objects.select_related(
#         "supplier",
#         "vendor",
#         "category_supplier_all",
#         "group_supplier",
#         "category_supplier",
#         "category",
#         "group",
#         "price",
#         "stock",
#     ).filter(check_to_order=True)[0:10]

#     context = {
#         "product_list": product_list,
#     }

#     return render(request, "product/catalog.html", context)


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

        supplier = self.forwarded.get("supplier", None)
        if supplier:
            qs = qs.filter(supplier=supplier)

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
        if supplier:
            qs = qs.filter(supplier=supplier)
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
