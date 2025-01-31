from dal import autocomplete
from django import forms

from apps.product.models import CategoryProduct, GroupProduct
from apps.supplier.models import (
    Discount,
    Supplier,
    SupplierCategoryProduct,
    SupplierCategoryProductAll,
    SupplierGroupProduct,
    Vendor,
)


class DiscountForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(), label="Поставщик"
    )

    vendor = forms.ModelChoiceField(
        queryset=Vendor.objects.all(),
        required=False,
        label="Производитель",
        # widget=autocomplete.ModelSelect2(
        #     url="supplier:vendor-autocomplete", forward=["supplier"]
        # ),
    )
    category_supplier = forms.ModelChoiceField(
        queryset=SupplierCategoryProduct.objects.all(),
        required=False,
        label="Категория",
        widget=autocomplete.ModelSelect2(
            url="supplier:category-autocomplete", forward=["supplier", "vendor"]
        ),
    )

    group_supplier = forms.ModelChoiceField(
        queryset=SupplierGroupProduct.objects.all(),
        required=False,
        label="Группа",
        widget=autocomplete.ModelSelect2(
            url="supplier:group-autocomplete",
            forward=["supplier", "vendor", "category_supplier"],
        ),
    )
    category_supplier_all = forms.ModelChoiceField(
        queryset=SupplierCategoryProductAll.objects.all(),
        required=False,
        label="Категория приходящая поставщика",
        widget=autocomplete.ModelSelect2(
            url="supplier:category-all-autocomplete",
            forward=["supplier", "vendor", "category_supplier", "group_supplier"],
        ),
    )

    class Meta:
        model = Discount
        fields = "__all__"
        # widgets = {
        #     "category_supplier": autocomplete.ModelSelect2(
        #         url="supplier:category-autocomplete", forward=["supplier", "vendor"]
        #     )
        # }

    # def __init__(self, *args, **kwargs):
    #     super(DiscountForm, self).__init__(*args, **kwargs)

    #     # self.fields['is_tag_pre_sale'].label = 'My new label'
    #     self.fields['is_tag_pre_sale'].widget = forms.CheckboxInput()


class SupplierCategoryProductAllAdminForm(forms.ModelForm):

    category_catalog = forms.ModelChoiceField(
        queryset=CategoryProduct.objects.all(), label="Категория Motrum"
    )

    group_catalog = forms.ModelChoiceField(
        queryset=GroupProduct.objects.all(),
        required=False,
        label="Группа Motrum",
        widget=autocomplete.ModelSelect2(
            url="supplier:group_catalog-autocomplete",
            forward=[
                "category_catalog",
            ],
        ),
    )

    class Meta:
        model = SupplierCategoryProductAll
        fields = "__all__"


class SupplierGroupProductAdminForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(), label="Поставщик"
    )
    vendor = forms.ModelChoiceField(queryset=Vendor.objects.all(), label="Вендор")

    category_supplier = forms.ModelChoiceField(
        queryset=SupplierCategoryProduct.objects.all(),
        required=False,
        label="Категория поставщика",
        widget=autocomplete.ModelSelect2(
            url="supplier:category-autocomplete",
            forward=[
                "supplier",
            ],
        ),
    )

    category_catalog = forms.ModelChoiceField(
        queryset=CategoryProduct.objects.all(), label="Категория Motrum"
    )

    group_catalog = forms.ModelChoiceField(
        queryset=GroupProduct.objects.all(),
        required=False,
        label="Группа Motrum",
        widget=autocomplete.ModelSelect2(
            url="supplier:group_catalog-autocomplete",
            forward=[
                "category_catalog",
            ],
        ),
    )

    class Meta:
        model = SupplierGroupProduct
        fields = "__all__"


class SupplierCategoryProductAdminForm(forms.ModelForm):

    category_catalog = forms.ModelChoiceField(
        queryset=CategoryProduct.objects.all(), label="Категория Motrum"
    )

    group_catalog = forms.ModelChoiceField(
        queryset=GroupProduct.objects.all(),
        required=False,
        label="Группа Motrum",
        widget=autocomplete.ModelSelect2(
            url="supplier:group_catalog-autocomplete",
            forward=[
                "category_catalog",
            ],
        ),
    )

    class Meta:
        model = SupplierCategoryProduct
        fields = "__all__"
