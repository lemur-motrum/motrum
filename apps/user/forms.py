from django import forms

from apps.user.models import AdminUser


class PasswordForm(forms.ModelForm):
    class Meta:
        model = AdminUser
        fields = "__all__"
        widgets = {
            "password": forms.PasswordInput(render_value=True),
        }

    # def __init__(self, *args, **kwargs):

    #     super(PasswordForm, self).__init__(*args, **kwargs)
    #     self.fields["password"].required = False

    # def clean(self):
    #     print(self.pk)
    #     item = self.cleaned_data
    #     # id_item = item.get("id")
    #     password = item.get("password")

    #     if password == "":
    #         print (1)
    #         raise forms.ValidationError(
    #             "Введите пароль"
    #         )
    #     else:
    #         return item


class LoginAdminForm(forms.Form):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = AdminUser
        fields = "__all__"
