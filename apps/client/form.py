from django import forms
from django.contrib import admin
from django.db import models
from apps.client.models import Requisites

class RequisitesAdminForm(forms.ModelForm):
    class Meta:
        model = Requisites
        fields = '__all__'
        widgets = {
            'postpay_persent_text': admin.widgets.AdminTextareaWidget(attrs={'rows': 4, 'cols': 80}),
            'postpay_persent_text_2': admin.widgets.AdminTextareaWidget(attrs={'rows': 4, 'cols': 80}),
            'postpay_persent_text_3': admin.widgets.AdminTextareaWidget(attrs={'rows': 4, 'cols': 80}),
          
        }