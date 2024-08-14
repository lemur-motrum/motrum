from django import forms


class SearchForm(forms.Form):
    search_input = forms.CharField(
        max_length=255,
        label="Введите данные о товаре",
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "autocomplete": "off",
                "placeholder": "Ведеите наименование или артикул",
            }
        ),
        required=False,
    )


class AuthForm(forms.Form):
    login_input = forms.CharField(
        max_length=255,
        label="Имя пользователя",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Имя",
            }
        ),
    )
    password_input = forms.CharField(
        max_length=255,
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-input",
                "placeholder": "Пароль",
            }
        ),
    )

    tel_input = forms.CharField(
        max_length=255,
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
                "placeholder": "Пароль",
            }
        ),
    )
