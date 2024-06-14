from dal import autocomplete
from django import forms


from apps.product.models import Product
from apps.specification.models import ProductSpecification
from apps.supplier.models import Supplier, Vendor


class PersonForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        label="Поставщик",
        help_text="Subject",
    )
    vendor = forms.ModelChoiceField(
        queryset=Vendor.objects.all(),
        required=False,
        label="Производитель",
        widget=autocomplete.ModelSelect2(
            url="specification:vendor-autocomplete", forward=["supplier"]
        ),
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        label="Товар",
        widget=autocomplete.ModelSelect2 (
                url="specification:product-autocomplete", forward=["supplier", "vendor"]
            ),
    )   
    # price_one = forms.FloatField(
    #     # required=False,
    #     label="цена за 1шт",
    #     widget=autocomplete.ModelSelect2(
    #         url="specification:price-one-autocomplete", forward=["product"]
    #     ),
    # )

    class Meta:

        model = ProductSpecification
        fields = "__all__"
        widgets = {
            # "product": autocomplete.ModelSelect2(
            #     url="specification:product-autocomplete", forward=["supplier", "vendor"]
            # ),
            "price_one": autocomplete.ListSelect2 (
                url="specification:price-one-autocomplete", forward=["product"]
            ),
        }
        
    # def __init__(self, *args, **kwargs):
    #     super(PersonForm, self).__init__(*args, **kwargs)
    #     # self.fields['supplier'].label = f"Поставщик  " f"Оно обозначается ."
    #     # for _, field in self.fields.items():
    #     #     field.widget.attrs['placeholder'] = field.help_text
    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)

        # if self.instance:
        #     self.fields['price_one'].initial = self.instance.price_one # or whatever you want the initial value to be
        #     self.fields['price_one'].choices = [(self.instance.price_one, self.instance.price_one)] # same values as above
