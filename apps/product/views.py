from django.shortcuts import render
from dal import autocomplete
from django.db.models import Q
from dal_select2.views import Select2ViewMixin
from dal.views import BaseQuerySetView
from regex import P

from apps import product
from apps.admin_specification.views import all_categories
from apps.product.models import (
    CategoryProduct,
    GroupProduct,
    Product,
    ProductProperty,
    Stock,
)
from apps.supplier.models import (
    SupplierCategoryProduct,
    SupplierCategoryProductAll,
    SupplierGroupProduct,
    Vendor,
)


# все категории
def catalog_all(request):
    category = CategoryProduct.objects.all().order_by("article_name")

    context = {
        "category": category,
        "title": "Каталог",
    }

    return render(request, "product/product_catalog.html", context)


# группы категорий
def catalog_group(request, category):

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
        vendor = Vendor.objects.filter()
        q_object = Q()
        q_object &= Q(check_to_order=True)
        if category is not None:
            q_object &= Q(category__slug=category)

        product_vendor = (
            Product.objects.select_related(
                "vendor",
                "category",
            )
            .filter(q_object)
            .distinct("vendor")
            .values("vendor", "vendor__name", "vendor__slug")
        )
        current_category = CategoryProduct.objects.get(slug=category)

        context = {
            "current_category": current_category,
            "product_vendor": product_vendor,
        }
        return render(request, "product/catalog.html", context)


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
    }

    return render(request, "product/catalog.html", context)


# страница отдельного продукта
def product_one(request, category, group, article):
    current_category = CategoryProduct.objects.get(slug=category)
    current_group = GroupProduct.objects.get(slug=group)
    product = Product.objects.get(article=article)
    product_properties = ProductProperty.objects.filter(product=product.pk)
    product_lot = Stock.objects.get(prod=product.pk)

    context = {
        "product": product,
        "current_category": current_category,
        "current_group": current_group,
        "title": product.name,
        "product_properties": product_properties,
        "product_lot": product_lot,
    }
    return render(request, "product/product_one.html", context)


def product_one_without_group(request, category, article):
    current_category = CategoryProduct.objects.get(slug=category)
    product = Product.objects.get(article=article)
    product_properties = ProductProperty.objects.filter(product=product.pk)
    product_lot = Stock.objects.get(prod=product.pk)

    context = {
        "product": product,
        "current_category": current_category,
        "title": product.name,
        "product_properties": product_properties,
        "product_lot": product_lot,
    }
    return render(request, "product/product_one.html", context)


# юрина вьюха каталога
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

    context = {
        "product_list": product_list,
    }

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
