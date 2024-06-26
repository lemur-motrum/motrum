from dal import autocomplete
from django import forms


from apps.product.models import CategoryProduct, GroupProduct, Product
from apps.specification.models import ProductSpecification
from apps.supplier.models import Supplier, SupplierCategoryProductAll, Vendor


class ProductForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(), label="Поставщик"
    )

    vendor = forms.ModelChoiceField(
        queryset=Vendor.objects.all(),
        required=False,
        label="Производитель",
        widget=autocomplete.ModelSelect2(
            url="product:vendor-autocomplete", forward=["supplier"]
        ),
    )
    category = forms.ModelChoiceField(
        queryset=CategoryProduct.objects.all(), label="Категория"
    )

    group = forms.ModelChoiceField(
        queryset=GroupProduct.objects.all(),
        required=False,
        label="Группа",
        widget=autocomplete.ModelSelect2(
            url="product:group-autocomplete", forward=["category"]
        ),
    )
    category_supplier_all = forms.ModelChoiceField(
        queryset=SupplierCategoryProductAll.objects.all(),
        label="Категория поставщика",
        widget=autocomplete.ModelSelect2(
            url="product:catesup-autocomplete",
            forward=["supplier", "vendor"],
            
        ),
    )

    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "cols": 150,
                    "rows": 7,
                }
            ),
        }
class ProductChangeForm(forms.ModelForm):
    

    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "cols": 150,
                    "rows": 7,
                }
            ),
            "name": forms.Textarea(
                attrs={
                    "cols": 150,
                    "rows": 2,
                }
            ),
           
        }
