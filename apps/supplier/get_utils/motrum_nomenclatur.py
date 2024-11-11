import datetime
import os
import re
import zipfile
import csv
from simple_history.utils import update_change_reason
from pytils import translit
from django.utils.text import slugify

from apps import supplier
from apps.core.models import Currency, Vat
from apps.logs.utils import error_alert

from apps.product.models import Lot, Price, Product, Stock
from apps.supplier.models import Supplier, Vendor
from project.settings import MEDIA_ROOT


def get_motrum_nomenclature():
    new_dir = "{0}/{1}".format(MEDIA_ROOT, "ones")
    path_nomenclature = f"{new_dir}/Справочник номенклатуры Мотрум.csv"

    fieldnames_nomenclature = [
        "Номенклатура",
        None,
        None,
        "Артикул",
        None,
        "Единица измерения",
        "Изготовитель",
        "Категория",
        "Описание",
        "Страна происхождения",
        "Производитель",
        "В группе",
    ]

    with open(path_nomenclature, "r", newline="", encoding="MACCYRILLIC") as csvfile:
        reader_nomenk = csv.DictReader(
            csvfile, delimiter=";", fieldnames=fieldnames_nomenclature
        )

        i = 0
        vendor = ""
        vendor_arr = []
        for row_nomenk in reader_nomenk:
            i += 1
            try:
                
                if ( i > 5000
                    and row_nomenk["Артикул"] != ""
                    and row_nomenk["Артикул"] != None and row_nomenk["В группе"] == "Emas"
                ):
                    vendor_row = str(row_nomenk["В группе"]).strip()

                    supplier_qs, vendor_qs = get_or_add_vendor(vendor_row)
                    
                    article_supplier = str(row_nomenk["Артикул"]).strip()
                    article_supplier = " ".join(article_supplier.split())
                    print(article_supplier)
                    lot_str = str(row_nomenk["Единица измерения"]).replace(".", "").strip()
                    lot = Lot.objects.get_or_create(
                        name_shorts=lot_str, defaults={"name": lot_str}
                    )[0]

                    name = str(row_nomenk["Номенклатура"]).strip()

                    description = None
                    if row_nomenk["Описание"] != "":
                        description = str(row_nomenk["Описание"]).strip()

                    # поиск товара в окт:

                    if vendor_qs.slug == "emas" or vendor_qs.slug == "tbloc":
                    
                        product = Product.objects.filter(
                            supplier=supplier_qs, article_supplier=article_supplier
                        )
                        
                        if product:
                            print(9999)
                            product = product[0]
                            product.vendor = vendor_qs
                            if (
                                product.name == article_supplier
                                and article_supplier != name
                            ):
                                product.name = name
                            if product.description != None and description:
                                product.description = description
                        else:
                            
                            product = add_new_product(
                                supplier_qs,
                                article_supplier,
                                vendor_qs,
                            )
                            product.name = name
                            product.description = description
                    else:
                        product = Product.objects.filter(
                            vendor=vendor_qs, article_supplier=article_supplier
                        )
                        
                        if product:
                            product = product[0]
                            if (
                                product.name == article_supplier
                                and article_supplier != name
                            ):
                                product.name = name
                            if product.description != None and description:
                                product.description = description
                        else:
                            product = add_new_product(
                                supplier_qs,
                                article_supplier,
                                vendor_qs,
                            )
                            product.name = name
                            product.description = description
                    product.autosave_tag = False
                    product._change_reason = "Автоматическое"
                    product.save()
                    
                    # update_change_reason(product, "Автоматическое")
                
                    add_stok_motrum_article(product,lot,)
            
            except Exception as e:
                print(e)
                error = "file_error"
                location = "Загрузка фаилов номенклатура "

                info = f"ошибка при чтении фаила{i}-{e}"
                e = error_alert(error, location, info)


def add_new_product(
    supplier_qs,
    article_supplier,
    vendor_qs,
):
    prod_new = Product(
        supplier=supplier_qs,
        name=article_supplier,
        vendor=vendor_qs,
        article_supplier=article_supplier,
        category_supplier_all=None,
        group_supplier=None,
        category_supplier=None,
        add_in_nomenclature=True,
    )
    prod_new.save()
    update_change_reason(prod_new, "Автоматическое")
    currency = Currency.objects.get(words_code="RUB")
    vat = Vat.objects.get(name=20)
    price =  Price(prod=prod_new,currency=currency,vat=vat,extra_price=True,in_auto_sale=False)
    price.save()
    update_change_reason(price, "Автоматическое")
    return prod_new


def get_or_add_vendor(vendor):
    vendor_name = vendor.strip()
    if vendor_name == "AuCom Electronics":
        vendor_name = "AuCom"
    elif vendor_name == "OptimusDrive":
        vendor_name = "Optimus Drive"
    elif vendor_name == "Delta":
        vendor_name = "Delta Electronics"

    slugish = translit.translify(vendor_name)
    slugish = slugify(slugish)

    try:
        vendor_qs = Vendor.objects.get(slug=slugish)
        supplier_qs = vendor_qs.supplier

    except Vendor.DoesNotExist:

        supplier_qs = Supplier.objects.get(slug="drugoe")
        vat_catalog = Vat.objects.get(name=20)
        currency_catalog = Currency.objects.get(words_code="RUB")

        vendor_qs = Vendor.objects.create(
            name=vendor_name,
            supplier=supplier_qs,
            vat_catalog=vat_catalog,
            currency_catalog=currency_catalog,
        )

    return (supplier_qs, vendor_qs)

def add_stok_motrum_article(product,lot,):
    product_stock = Stock.objects.get_or_create(
        prod=product,
        defaults={
            "lot": lot,
        },
    )

    stock = product_stock[0]

    stock.save()
    