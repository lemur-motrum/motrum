from django.shortcuts import render
from dal import autocomplete

from apps import supplier
from apps.product.models import Product
from apps.supplier.models import Vendor
from django.db.models import Q


# Create your views here.
class ProductAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Product.objects.all()

        supplier = self.forwarded.get("supplier", None)
        if supplier:
            qs = qs.filter(supplier=supplier)

        vendor = self.forwarded.get("vendor", None)
        if vendor:
            qs = qs.filter(vendor=vendor)

        if self.q:
            # name__icontains=self.q
            qs = qs.filter(
                Q(name__icontains=self.q)
                | Q(article__icontains=self.q)
                | Q(article_supplier__icontains=self.q)
                | Q(additional_article_supplier__icontains=self.q)
            )

        return qs



class CountryAutocomplete(autocomplete.Select2QuerySetView):
    pass


class VendorAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Vendor.objects.all()
        supplier = self.forwarded.get("supplier", None)

        if supplier:
            qs = qs.filter(supplier=supplier)

        if self.q:
            qs = qs.filter(name=self.q)

        return qs
