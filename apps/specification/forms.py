from dal import autocomplete
from django import forms


from apps.product.models import Price, Product
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
        widget=autocomplete.ModelSelect2(
            url="specification:product-autocomplete",
            forward=["supplier", "vendor"],
        ),
    )

    class Meta:

        model = ProductSpecification
        fields = "__all__"
        widgets = {
            "price_one": autocomplete.ListSelect2(
                url="specification:price-one-autocomplete",
                forward=["product"],
                attrs={},
            )
        }

    class Media:
        css = {
            "all": ("specification/css/admin_price_exclusive.css",),
        }

    def __init__(self, *args, **kwargs):
        super(PersonForm, self).__init__(*args, **kwargs)
        if self.instance.pk is not None:
            self.fields["product"].widget.attrs = {"data-readonly": "1"}
