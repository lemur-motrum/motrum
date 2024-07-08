from typing import Any
from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


class SearchForm(forms.Form):
    search_input = forms.CharField(
        max_length=255,
        label="Введите данные о товаре",
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
            }
        ),
        required=False,
    )
