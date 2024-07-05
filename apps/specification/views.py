from django import http
from django.shortcuts import redirect, render
from dal import autocomplete

from apps import supplier
from apps.product.models import Price, Product
from apps.specification.forms import PersonForm
from apps.specification.models import ProductSpecification
from apps.supplier.models import Vendor
from django.db.models import Q


class ProductAutocomplete(autocomplete.Select2QuerySetView):
    # def save_specification_view_admin():
    #     id_bitrix
    #     admin_creator
    #     specification = Specification(
    #         id_bitrix = id_bitrix
    #         admin_creator = admin_creator
    #     )
    
    
    def get_result_value(self, result):
   
        """Return the value of a result."""
        return str(result.pk)

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


class PriceOneAutocomplete(autocomplete.Select2QuerySetView):
    def get_result_value(self, result):
   
        """Return the value of a result."""
        print(result.rub_price_supplier)
        return str(result.rub_price_supplier)

    def get_queryset(self):

        qs = []

        product = self.forwarded.get("product", None)

        if product:
            qs = Price.objects.all()
            qs = qs.filter(prod=product)

        return qs

    def create_object(self, text):
        product = self.forwarded.get("product", None)
        prod = ProductSpecification(
            product_id=product, price_one=text, price_exclusive=True
        )
        prod.save()

        return prod

    def post(self, request, *args, **kwargs):
        """
        Create an object given a text after checking permissions.

        Runs self.validate() if self.validate_create is True.
        """

        text = request.POST.get("text", None)

        if text is None:
            return http.HttpResponseBadRequest()

        return http.JsonResponse(
            {
                "text": text,
            }
        )
