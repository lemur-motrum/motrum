from locale import currency
from django.contrib import admin

from apps.core.models import (
    BaseImage,
    BaseInfo,
    BaseInfoAccountRequisites,
    CompanyInfoWeb,
    CompanyPrijectAutoInfoWeb,
    Currency,
    CurrencyPercent,
    IndexInfoWeb,
    PhotoClientInfoWeb,
    PhotoEmoloeeInfoWeb,
    ReviewsAutoInfoWeb,
    SeoTextSolutions,
    SliderMain,
    TypeDelivery,
    Vat,
)
from apps.product.admin import LotAdmin
from apps.product.models import Lot
from project.admin import website_admin


class CurrencyPercentAdmin(admin.ModelAdmin):
    # model = CurrencyPercent
    # list_display = ("percent",)

    def has_add_permission(
        self,
        request,
    ):
        currency = CurrencyPercent.objects.filter().exists()
        if currency == True:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        return False


class CurrencyAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return False


class VatAdmin(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return False


class BaseInfoAccountRequisitesInline(admin.TabularInline):
    model = BaseInfoAccountRequisites


class BaseInfoAdmin(admin.ModelAdmin):
    inlines = [
        BaseInfoAccountRequisitesInline,
    ]

    def has_delete_permission(self, request, obj=None):
        return False
    
class BaseImageAdmin(admin.ModelAdmin):
    def has_add_permission(
        self,
        request,
    ):
        img = BaseImage.objects.filter().exists()
        if img == True:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        return False


class TypeDeliveryAdmin(admin.ModelAdmin):
    list_display = ("text", "text_long", "company_delivery","actual")
    
    def has_delete_permission(self, request, obj=None):
        return False


# АДМИНКА ДЛЯ ВЕБСАЙТА
class SliderMainAdminWeb(admin.ModelAdmin):
    list_display = [
        "name",
        "type_slider",
        "active",
    ]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "name",
                    "type_slider",
                ]
            },
        )
    ]

    def get_fieldsets(self, request, obj):
        fields = super(SliderMainAdminWeb, self).get_fieldsets(request, obj)
        # slider = SliderMain.objects.filter(prod=obj).exists()
        slider_main = [
            (
                "Текст в слайде",
                {
                    "fields": [
                        "article",
                        "name",
                        "active",
                        "image",
                        ("image_right", "video", "video_file"),
                        (
                            "text1",
                            "text2",
                        ),
                        (
                            "text4",
                            "icon3",
                        ),
                    ]
                },
            )
        ]
        if obj:
            if obj.type_slider == "MAIN":
                return slider_main
        else:
            return fields

    def get_exclude(self, request, obj=None):

        if obj:
            if obj.product_promote:
                return ["video", "slug"]
            else:
                return ["product_promote", "slug"]
        else:
            return ["product_promote", "slug"]

    def has_delete_permission(self, request, obj=None):
        return False


class IndexInfoWebAdminWeb(admin.ModelAdmin):
    # model = CurrencyPercent
    # list_display = ("percent",)

    def has_add_permission(
        self,
        request,
    ):
        info_web = IndexInfoWeb.objects.filter().exists()
        if info_web == True:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        return False


class CompanyInfoWebAdminWeb(admin.ModelAdmin):
    # model = CurrencyPercent
    # list_display = ("percent",)

    def has_add_permission(
        self,
        request,
    ):
        info_web = CompanyInfoWeb.objects.filter().exists()
        if info_web == True:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        return False


class CompanyPrijectAutoInfoWebAdminWeb(admin.ModelAdmin):
    # model = CurrencyPercent
    # list_display = ("percent",)

    def has_add_permission(
        self,
        request,
    ):
        info_web = CompanyPrijectAutoInfoWeb.objects.filter().exists()
        if info_web == True:
            return False
        else:
            return True

    def has_delete_permission(self, request, obj=None):
        return False


class ReviewsAutoInfoWebAdminWeb(admin.ModelAdmin):

    def has_delete_permission(self, request, obj=None):
        return False


class SeoTextSolutionsAdminWeb(admin.ModelAdmin):
    list_display = (
        "name_page",
        "text",
    )


# Register your models here.

admin.site.register(BaseImage,BaseImageAdmin)
admin.site.register(BaseInfo, BaseInfoAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(CurrencyPercent, CurrencyPercentAdmin)
admin.site.register(Vat, VatAdmin)
admin.site.register(TypeDelivery, TypeDeliveryAdmin)

website_admin.register(SliderMain, SliderMainAdminWeb)
website_admin.register(IndexInfoWeb, IndexInfoWebAdminWeb)
# website_admin.register(SeoTextSolutions, SeoTextSolutionsAdminWeb)
website_admin.register(CompanyInfoWeb, CompanyInfoWebAdminWeb)
website_admin.register(CompanyPrijectAutoInfoWeb, CompanyPrijectAutoInfoWebAdminWeb)
# website_admin.register(ReviewsAutoInfoWeb, ReviewsAutoInfoWebAdminWeb)
website_admin.register(PhotoClientInfoWeb)
website_admin.register(PhotoEmoloeeInfoWeb)
