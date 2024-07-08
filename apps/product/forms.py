from dal import autocomplete
from django import forms


from apps.product.models import CategoryProduct, GroupProduct, Product
from apps.specification.models import ProductSpecification
from apps.supplier.models import (
    Supplier,
    SupplierCategoryProduct,
    SupplierCategoryProductAll,
    SupplierGroupProduct,
    Vendor,
)


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
        queryset=CategoryProduct.objects.all(), label="Категория Motrum",required=False,
    )

    group = forms.ModelChoiceField(
        queryset=GroupProduct.objects.all(),
        required=False,
        label="Группа Motrum",
        widget=autocomplete.ModelSelect2(
            url="product:group-autocomplete", forward=["category"]
        ),
    )
    category_supplier = forms.ModelChoiceField(
        required=False,
        queryset=SupplierCategoryProduct.objects.all(), label="Категория поставщика",
        widget=autocomplete.ModelSelect2(
            url="product:category_supplier-autocomplete", forward=["supplier"]
        ),
    )

    group_supplier = forms.ModelChoiceField(
        queryset=SupplierGroupProduct.objects.all(),
        required=False,
        label="Группа поставщика",
        widget=autocomplete.ModelSelect2(
            url="product:group_supplier-autocomplete", forward=["category_supplier"]
        ),
    )

    category_supplier_all = forms.ModelChoiceField(
        queryset=SupplierCategoryProductAll.objects.all(),
        required=False,
        label="Подгруппа поставщика",
        widget=autocomplete.ModelSelect2(
            url="product:category_supplier_all-autocomplete",
            forward=["supplier", "vendor","category_supplier","group_supplier"],
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
            "additional_article_supplier": forms.Textarea(
                attrs={
                    "cols": 50,
                    "rows": 2,
                }
            ),
            "group": forms.Select(
                attrs={
                }
            ),
        }
        
        
    def __init__(self, *args, **kwargs):
        super(ProductChangeForm, self).__init__(*args, **kwargs)
        print(self.instance.pk)
        prod = Product.objects.filter(id=self.instance.pk).values()
        
        for product_item in prod:
                product_blank_dict = {
                    k: v for k, v in product_item.items() if v == None
                }

                for item_dict in product_blank_dict:
                    verbose_name = Product._meta.get_field(item_dict).name
                    item_one = f"<li >{verbose_name}</li>"
                   
                    print(item_one)
                    self.fields[verbose_name].widget.attrs = {'class': 'special_item_none' ,'placeholder': 'username',}
                    self.fields[verbose_name].label = {'class': 'special_item_none',}
                    
        
  