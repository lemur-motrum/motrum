from dal import autocomplete
from django import forms


from apps.product.models import Product
from apps.specification.models import ProductSpecification
from apps.supplier.models import Supplier, Vendor


class PersonForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(queryset=Supplier.objects.all(), required=False, label="Поставщик")
    vendor = forms.ModelChoiceField(
        queryset=Vendor.objects.all(),
        required=False,
        label="Производитель",
        widget=autocomplete.ModelSelect2(
            url="specification:vendor-autocomplete", forward=["supplier"]
        ),
    )
   

    class Meta:
       
        model = ProductSpecification
        fields = "__all__"
        widgets = {
            "product": autocomplete.ModelSelect2(
                url="specification:product-autocomplete", forward=["supplier", "vendor"])
            
        }
   
        
   