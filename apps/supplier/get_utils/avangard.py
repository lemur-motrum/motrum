from locale import currency
import os
import re
from unicodedata import category
import openpyxl as openxl
from openpyxl import Workbook
from openpyxl import load_workbook

from apps import supplier
from apps.core.models import Vat


from apps.logs.utils import error_alert
from apps.product.models import Price, Product
from apps.supplier.models import Supplier, SupplierCategoryProductAll, Vendor
from project.settings import BASE_DIR



def get_avangard_file():
    supplier = Supplier.objects.get(slug="avangard")
    vendor = Vendor.objects.get(supplier=supplier, slug="odot-automation")

    file_path = os.path.join(BASE_DIR, "tmp/Odot.xlsx")
    excel_doc = openxl.open(filename=file_path, data_only=True)

    sheetnames = excel_doc.sheetnames
    sheet = excel_doc[sheetnames[0]]
    first = 0
    category = ""
    category_item = None
    for i in range(sheet.min_row, sheet.max_row + 1):
        
        if first == 0:
            if sheet[f"A{i}"].value == "P/N\nАртикул":
                first = i
            
        elif first != 0:
            # запись категорий
            if sheet[f"C{i}"].value is None and sheet[f"b{i}"].value is None and sheet[f"a{i}"].value is not None:
                # print(sheet[f"b{i}"].value)
                category = sheet[f"A{i}"].value
                category_item = get_category_avangard(category, supplier, vendor)
             
            elif sheet[f"C{i}"].value is None and sheet[f"b{i}"].value is None and sheet[f"a{i}"].value is None:
                category_item = None
            # запись товаров
            elif (
                sheet[f"a{i}"].value is not None
                and sheet[f"b{i}"].value is not None
                and sheet[f"c{i}"].value is not None
            ):
                article_supplier = sheet[f"A{i}"].value
                price_supplier_noval = sheet[f"C{i}"].value

                price_supplier_sub = re.sub(
                    "[^0-9.,]", "", price_supplier_noval
                ).replace(",", ".")
                price_supplier = float(price_supplier_sub)

                product = Product.objects.filter(
                    supplier=supplier,
                    vendor=vendor,
                    article_supplier=article_supplier,
                ).exists()

                name = sheet[f"B{i}"].value

                if product:
                    article = Product.objects.get(article_supplier=article_supplier)

                    product_item = Product.objects.filter(
                        article_supplier=article_supplier,
                        supplier=supplier,
                        vendor=vendor,
                    ).update(name=name, category_supplier_all=category_item)

                else:
                    article = Product.objects.create(
                        article_supplier=article_supplier,
                        supplier=supplier,
                        vendor=vendor,
                        name=name,
                        category_supplier_all=category_item,
                    )

                peice = get_price_avangard(
                    vendor, supplier, article, price_supplier, category_item
                )
            # обработка ошибок считыввания
            else:
                error = "file structure"
                location=f"Загрузка фаилов авангард строка:{i}"
                info="Фаил не соответствует обрабатываемой структуре фаила-считывание фаила невозможно"
                e = error_alert(error,location,info)

    if first == 0:
        error = "file structure"
        location="Загрузка фаилов авангард"
        info="Фаил не соответствует обрабатываемой структуре фаила-считывание фаила невозможно"
        e = error_alert(error,location,info)
        

def get_category_avangard(name, supplier, vendor):
    try:
        category_item = SupplierCategoryProductAll.objects.get(
            supplier=supplier, vendor=vendor, name=category
        )
        return category_item

    except SupplierCategoryProductAll.DoesNotExist:
        category_item = SupplierCategoryProductAll.objects.create(
            name=category,
            supplier=supplier,
            vendor=vendor,
        )
        return category_item


def get_price_avangard(vendor, supplier, product, price_supplier, category_item):
    from apps.core.utils import get_price_supplier_rub, get_category, get_price_motrum

    currency = vendor.currency_catalog.words_code
    vat_include = True
    vat = Vat.objects.get(name=20)

    rub_price_supplier = get_price_supplier_rub(
        currency,
        vat,
        vat_include,
        price_supplier,
    )
    item_category_all = get_category(supplier.id, vendor, category_item)

    item_category = item_category_all[0]
    item_group = item_category_all[1]
    price_motrums = get_price_motrum(
        item_category, item_group, vendor, rub_price_supplier, category_item
    )
    price_motrum = price_motrums[0]
    sale = price_motrums[1]
    price = Price.objects.update_or_create(
        prod=product,
        defaults={
            "rub_price_supplier": rub_price_supplier,
            "price_motrum": price_motrum,
            "sale": sale,
        },
        create_defaults={
            "currency": vendor.currency_catalog,
            "vat": vat,
            "vat_include": vat_include,
            "price_supplier": price_supplier,
        },
    )


# get_avangard_file()
