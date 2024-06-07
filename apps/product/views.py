from unicodedata import category
from django.shortcuts import render
from dal import autocomplete
from django.db.models import Q
from dal_select2.views import Select2ViewMixin
from dal.views import BaseQuerySetView

from apps.product.models import CategoryProduct, GroupProduct, Product
from apps.supplier.models import SupplierCategoryProductAll, Vendor


class VendorAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = Vendor.objects.all()

        supplier = self.forwarded.get("supplier", None)

        if supplier:
            qs = qs.filter(supplier=supplier)

        vendor = self.forwarded.get("vendor", None)
        if vendor:
            qs = qs.filter(vendor=vendor)

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

        return qs


class CategSupAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = SupplierCategoryProductAll.objects.all()

        supplier = self.forwarded.get("supplier", None)

        if supplier:
            qs = qs.filter(supplier=supplier)
            
            

        vendor = self.forwarded.get("vendor", None)
        if vendor:
            qs = qs.filter(vendor=vendor)
            
        # category_supplier = self.forwarded.get("category_supplier", None)

        # if supplier:
        #     qs = qs.filter(category_supplier=category_supplier)
        
        
        
        if self.q:
            # name__icontains=self.q
            qs = qs.filter(
                Q(name=self.q)
                | Q(name__icontains=self.q)
                # | Q(article_supplier__icontains=self.q)
                # | Q(additional_article_supplier__icontains=self.q)
            )

        return qs
