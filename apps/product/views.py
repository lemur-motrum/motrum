from unicodedata import category
from django.shortcuts import render
from dal import autocomplete
from django.db.models import Q
from dal_select2.views import Select2ViewMixin
from dal.views import BaseQuerySetView

from apps.product.models import CategoryProduct, GroupProduct, Product
from apps.supplier.models import SupplierCategoryProduct, SupplierCategoryProductAll, SupplierGroupProduct, Vendor


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
            qs = qs.filter(
                Q(name__icontains=self.q)
            )

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
            qs = qs.filter(
                Q(name__icontains=self.q)
            )

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
            qs = qs.filter(
                Q(name__icontains=self.q)
            )    
       
        
       

        return qs

class SupplierCategoryProductAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = SupplierCategoryProduct.objects.all()
        supplier = self.forwarded.get("supplier", None)
        if supplier:
            qs = qs.filter(supplier=supplier)
        if self.q:
            # name__icontains=self.q
            qs = qs.filter(
                Q(name__icontains=self.q)
            )    
        return qs
    

class SupplierGroupProductAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        qs = SupplierGroupProduct.objects.all()
        category_supplier = self.forwarded.get("category_supplier", None)
        if category_supplier:
            qs = qs.filter(category_supplier=category_supplier)
        if self.q:
            # name__icontains=self.q
            qs = qs.filter(
                Q(name__icontains=self.q)
            )    
        return qs    
    