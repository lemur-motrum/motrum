from unicodedata import category
from click import group
from django.shortcuts import render
from dal import autocomplete
from django.db.models import Q
from dal_select2.views import Select2ViewMixin
from dal.views import BaseQuerySetView
from regex import P

from apps import product
from apps.product.models import CategoryProduct, GroupProduct, Product
from apps.supplier.models import (
    SupplierCategoryProduct,
    SupplierCategoryProductAll,
    SupplierGroupProduct,
    Vendor,
)

# все категории
def catalog_all(request):
    category = CategoryProduct.objects.all().order_by("article_name")

    context = {"category": category}

    return render(request, "product/product_catalog.html", context)

# группы категорий
def catalog_group(request, category):

    group = GroupProduct.objects.filter(category__slug=category).order_by("article_name")

    context = {"category": category, "group": group}

    return render(request, "product/product_group.html", context)

# страница всех продуктов в категории\группе
def products_items(request, category, group):
    vendor = Vendor.objects.filter()
    q_object = Q()
    q_object &= Q(check_to_order=True)
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
        .distinct("vendor")
        .values("vendor", "vendor__name", "vendor__slug")
    )
    category = CategoryProduct.objects.get(slug=category)
    group = GroupProduct.objects.get(slug=group)
    context = {
        "category": category.id, 
        "group": group.id, 
        "product_vendor": product_vendor,}

    return render(request, "product/catalog.html", context)

# страница отдельного продукта
def product_one(request,category, group, article):
    product = Product.objects.get(article=article)
    context = {"product":product}
    return render(request, "product/product_one.html", context)


#юрина вьюха каталога
def catalog(request):

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
    ).filter(check_to_order=True)[0:10]

    context = {"product_list": product_list}

    return render(request, "product/catalog.html", context)


# автозаполнения для админки бек окт
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
