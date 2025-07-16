import traceback
import openpyxl
import re
import pandas as pd

from apps.core.utils import (
    serch_prod_to_motrum_props_article,
    serch_prod_to_motrum_props_categ,
    serch_props_prod_and_add_motrum_props,
    serch_props_prod_and_add_motrum_props_diapason,
)
from apps.logs.utils import error_alert
from apps.product.models import (
    Product,
    ProductPropertyMotrum,
    ProductPropertyValueMotrum,
    VendorPropertyAndMotrum,
)
from apps.supplier.models import Supplier
from project.settings import MEDIA_ROOT


def xlsx_props_motrum():

    try:
        print(2)

        def smart_cast(x):
            try:
                return int(x)
            except ValueError:
                try:
                    return float(x.replace(",", "."))
                except ValueError:
                    return x

        # Открываем исходный файл
        input_path = f"{MEDIA_ROOT}/documents/filter/filter_comma2.xlsx"
        wb = openpyxl.load_workbook(input_path)
        sheet_names = wb.sheetnames

        for sheet_name in sheet_names:
            print(sheet_name)
            if (
                sheet_name == "РromPower (привод.техника) ПЧ "
                or "РromPower (привод.техника) УПП "
                or "PromPower  (Резисторы и "
                or "PP (привод.техника)Синус-фильтр"
            ):
                supplier_sheets = Supplier.objects.get(slug="prompower")
            elif sheet_name == "ONI ":
                supplier_sheets = Supplier.objects.get(slug="iek")

            if sheet_name == "Характеристики Мотрум ":
                continue  # пропускаем этот лист

            ws = wb[sheet_name]

            print(f"Обрабатывается лист: {sheet_name}")

            prev_name_motrum = None
            prev_supplier = None
            prev_name_supplier = None
            not_product = []
            for idx, row in enumerate(
                ws.iter_rows(min_row=2, min_col=1, max_col=8, values_only=True), start=2
            ):

                print(3)
                try:
                    if idx > 10:

                        (
                            name_motrum,
                            value_motrum,
                            supplier,
                            name_supplier,
                            value_supplier,
                            unit,
                            values,
                            articles,
                        ) = [str(x).strip() if x is not None else None for x in row]

                        # Если есть значение в value_motrum
                        if value_motrum:
                            # Если name_motrum пустой, берем из предыдущей строки
                            if not name_motrum:
                                name_motrum = prev_name_motrum
                            else:
                                prev_name_motrum = name_motrum
                            # Если supplier пустой, берем из предыдущей строки
                            if not supplier:
                                supplier = prev_supplier
                            else:
                                prev_supplier = supplier
                            # Если name_supplier пустой, берем из предыдущей строки
                            if not name_supplier:
                                name_supplier = prev_name_supplier
                            else:
                                prev_name_supplier = name_supplier
                        else:
                            # Если value_motrum пустой, не обновляем prev_* значения
                            pass

                        print("Наименование характеристик Мотрум:", name_motrum)
                        print("Вариант значений мотрум:", value_motrum)
                        print("Поставщик:", supplier)
                        print("Название характеристики поставщика:", name_supplier)
                        print("Вариант значений поставщика:", value_supplier)
                        print("Единица измерения (если есть):", unit)
                        print("Значения:", values)
                        print("артикул:", articles)

                        type_save = "normal"
                        if value_motrum == "диапазон":
                            is_diapason = True
                            type_save = "diapason"
                        else:
                            is_diapason = False

                        if values == "Одинаковые значения":
                            is_more_val = True
                            type_save = "multi"
                        else:
                            is_more_val = False

                        if values == "артикулы":
                            is_article = True
                            type_save = "article"
                        else:
                            is_article = False

                        print(type_save)

                        # стандарт значение с непустыми полями
                        if (
                            type_save == "normal"
                            and name_supplier
                            and value_supplier != "-"
                        ):

                            prod_prop_motrum, prod_prop_value_motrum = (
                                create_motrum_props(
                                    name_motrum, value_motrum, is_diapason
                                )
                            )
                            vendor_property_and_motrum, created = (
                                create_motrum_props_and_vendor(
                                    supplier_sheets,
                                    None,
                                    prod_prop_motrum,
                                    prod_prop_value_motrum,
                                    name_supplier,
                                    value_supplier,
                                    is_diapason,
                                    False
                                )
                            )
                            serch_props_prod_and_add_motrum_props(
                                vendor_property_and_motrum, supplier_sheets
                            )

                        # множественное значение в вариантах
                        if type_save == "multi":

                            val = value_motrum.split("||")
                            for val_item in val:
                                val_item = val_item.strip()
                                prod_prop_motrum, prod_prop_value_motrum = (
                                    create_motrum_props(
                                        name_motrum, val_item, is_diapason
                                    )
                                )
                                vendor_property_and_motrum, created = (
                                    create_motrum_props_and_vendor(
                                        supplier_sheets,
                                        None,
                                        prod_prop_motrum,
                                        prod_prop_value_motrum,
                                        name_supplier,
                                        val_item,
                                        is_diapason,
                                        False
                                    )
                                )
                                serch_props_prod_and_add_motrum_props(
                                    vendor_property_and_motrum, supplier_sheets
                                )

                        # if type_save == "article":
                        #     prod_prop_motrum, prod_prop_value_motrum = create_motrum_props(
                        #         name_motrum, value_motrum, is_diapason
                        #     )
                        #     articles = articles.split(",")
                        #     for article in articles:
                        #         article = article.strip()

                        #         if supplier_sheets.slug == "prompower":
                        #             article_rpl = article.replace("-", "")
                        #         elif  supplier_sheets.slug == "iek":
                        #             article_rpl = article

                        #         serch_prod_to_motrum_props_article(
                        #             prod_prop_motrum,
                        #             prod_prop_value_motrum,
                        #             article_rpl,
                        #             supplier_sheets,
                        #             is_diapason,
                        #         )
                        #         products = Product.objects.filter(supplier=supplier_sheets,article_supplier=article_rpl)
                        #         if products:
                        #             pass
                        #         else:
                        #             if article not in not_product:
                        #                 not_product.append(article)

                        # if type_save == "diapason":
                        #     prod_prop_motrum, prod_prop_value_motrum = create_motrum_props(
                        #         name_motrum, value_motrum, is_diapason
                        #     )
                        #     vendor_property_and_motrum,created = create_motrum_props_and_vendor(
                        #                     supplier_sheets,
                        #                     None,
                        #                     prod_prop_motrum,
                        #                     None,
                        #                     name_supplier,
                        #                     None,
                        #                     is_diapason,
                        #                 )
                        #     serch_props_prod_and_add_motrum_props_diapason(vendor_property_and_motrum,supplier_sheets)

                        print("-----")
                except Exception as e:
                    print(e)
                    tr = traceback.format_exc()
                    error = "file_error"
                    location = "РАзбор х-к мотрум из фаила"

                    info = f"Конкретный товар строка {sheet_name}{idx}{row}{e}{tr}"
                    e = error_alert(error, location, info)
            print(not_product)
    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        error = "file_error"
        location = "РАзбор х-к мотрум из фаила"

        info = f"общая{e}{tr}"
        e = error_alert(error, location, info)


def create_motrum_props(name_motrum, value_motrum, is_diapason):
    prod_prop_motrum, created = ProductPropertyMotrum.objects.get_or_create(
        name=name_motrum, is_diapason=is_diapason
    )

    if prod_prop_motrum.is_diapason:
        prod_prop_value_motrum, created = (
            ProductPropertyValueMotrum.objects.get_or_create(
                property_motrum=prod_prop_motrum, is_diapason=is_diapason
            )
        )
    else:
        prod_prop_value_motrum, created = (
            ProductPropertyValueMotrum.objects.get_or_create(
                property_motrum=prod_prop_motrum, value=value_motrum
            )
        )

    return (prod_prop_motrum, prod_prop_value_motrum)


def create_motrum_props_and_vendor(
    supplier,
    vendor,
    property_motrum,
    property_value_motrum,
    name_supplier,
    value_supplier,
    is_diapason,
    is_category
):
    obj, created = VendorPropertyAndMotrum.objects.get_or_create(
        supplier=supplier,
        property_motrum=property_motrum,
        property_value_motrum=property_value_motrum,
        property_vendor_name=name_supplier,
        property_vendor_value=value_supplier,
        is_diapason=is_diapason,
        is_category=is_category
    )
    print("create_motrum_props_and_vendor", obj, created)
    return (obj, created)


def xlsx_props_motrum_pandas():
    try:
        input_path = f"{MEDIA_ROOT}/documents/filter/filter_comma2.xlsx"
        df_dict = pd.read_excel(input_path, sheet_name=None, dtype=str)
        for sheet_name, df in df_dict.items():
            print(sheet_name)
            if sheet_name == "РromPower (привод.техника) ПЧ ":
                supplier_sheets = Supplier.objects.get(slug="prompower")
            elif sheet_name == "ONI ":
                supplier_sheets = Supplier.objects.get(slug="iek")
            if sheet_name == "Характеристики Мотрум ":
                continue  # пропускаем этот лист
            if sheet_name != "ONI ":
                continue  # пропускаем этот лист
            print(f"Обрабатывается лист: {sheet_name}")
            prev_name_motrum = None
            prev_supplier = None
            prev_name_supplier = None
            not_product = []
            for idx, row in df.iterrows():
                try:
                    # pandas индексация с 0, Excel с 2, поэтому idx+2
                    if idx + 2 == 14:
                        print(type(row.iloc[4]))
                        name_motrum = str(row[0]).strip() if pd.notna(row[0]) else None
                        value_motrum = str(row[1]).strip() if pd.notna(row[1]) else None
                        supplier = str(row[2]).strip() if pd.notna(row[2]) else None
                        name_supplier = (
                            str(row[3]).strip() if pd.notna(row[3]) else None
                        )
                        value_supplier = (
                            str(row[4]).strip() if pd.notna(row[4]) else None
                        )
                        unit = str(row[5]).strip() if pd.notna(row[5]) else None
                        values = str(row[6]).strip() if pd.notna(row[6]) else None
                        articles = str(row[7]).strip() if pd.notna(row[7]) else None
                        category = str(row[8]).strip() if pd.notna(row[7]) else None
                        if value_motrum:
                            if not name_motrum:
                                name_motrum = prev_name_motrum
                            else:
                                prev_name_motrum = name_motrum
                            if not supplier:
                                supplier = prev_supplier
                            else:
                                prev_supplier = supplier
                            if not name_supplier:
                                name_supplier = prev_name_supplier
                            else:
                                prev_name_supplier = name_supplier
                        print("Наименование характеристик Мотрум:", name_motrum)
                        print("Вариант значений мотрум:", value_motrum)
                        print("Поставщик:", supplier)
                        print("Название характеристики поставщика:", name_supplier)
                        print("Вариант значений поставщика:", value_supplier)
                        print("Единица измерения (если есть):", unit)
                        print("Значения:", values)
                        print("Список товаров:", articles)
                        print("Категория группы :", category)
                        type_save = "normal"
                        if value_motrum == "диапазон":
                            is_diapason = True
                            type_save = "diapason"
                        else:
                            is_diapason = False
                        if values == "Одинаковые значения":
                            is_more_val = True
                            type_save = "multi"
                        else:
                            is_more_val = False
                        if values == "артикулы":
                            is_article = True
                            type_save = "article"
                        if values == "Группа":
                            is_article = True
                            type_save = "categ"
                        else:
                            is_article = False
                        print(type_save)
                        if (
                            type_save == "normal"
                            and name_supplier
                            and value_supplier != "-"
                        ):
                            prod_prop_motrum, prod_prop_value_motrum = (
                                create_motrum_props(
                                    name_motrum, value_motrum, is_diapason
                                )
                            )
                            vendor_property_and_motrum, created = (
                                create_motrum_props_and_vendor(
                                    supplier_sheets,
                                    None,
                                    prod_prop_motrum,
                                    prod_prop_value_motrum,
                                    name_supplier,
                                    value_supplier,
                                    is_diapason,
                                    False
                                )
                            )
                            serch_props_prod_and_add_motrum_props(
                                vendor_property_and_motrum, supplier_sheets
                            )
                        if type_save == "multi":
                            val = value_motrum.split("||")
                            for val_item in val:
                                val_item = val_item.strip()
                                prod_prop_motrum, prod_prop_value_motrum = (
                                    create_motrum_props(
                                        name_motrum, val_item, is_diapason
                                    )
                                )
                                vendor_property_and_motrum, created = (
                                    create_motrum_props_and_vendor(
                                        supplier_sheets,
                                        None,
                                        prod_prop_motrum,
                                        prod_prop_value_motrum,
                                        name_supplier,
                                        val_item,
                                        is_diapason,
                                        False
                                    )
                                )
                                serch_props_prod_and_add_motrum_props(
                                    vendor_property_and_motrum, supplier_sheets
                                )

                        if type_save == "article":
                            prod_prop_motrum, prod_prop_value_motrum = (
                                create_motrum_props(
                                    name_motrum, value_motrum, is_diapason
                                )
                            )
                            if articles:
                                articles_list = articles.split(",")
                                for article in articles_list:
                                    article = article.strip()
                                    if supplier_sheets.slug == "prompower":
                                        article_rpl = article.replace("-", "")
                                    elif supplier_sheets.slug == "iek":
                                        article_rpl = article
                                    else:
                                        article_rpl = article
                                    serch_prod_to_motrum_props_article(
                                        prod_prop_motrum,
                                        prod_prop_value_motrum,
                                        article_rpl,
                                        supplier_sheets,
                                        is_diapason,
                                    )
                                    products = Product.objects.filter(
                                        supplier=supplier_sheets,
                                        article_supplier=article_rpl,
                                    )
                                    if not products:
                                        if article not in not_product:
                                            not_product.append(article)
                        if type_save == "diapason":
                            prod_prop_motrum, prod_prop_value_motrum = (
                                create_motrum_props(
                                    name_motrum, value_motrum, is_diapason
                                )
                            )
                            vendor_property_and_motrum, created = (
                                create_motrum_props_and_vendor(
                                    supplier_sheets,
                                    None,
                                    prod_prop_motrum,
                                    None,
                                    name_supplier,
                                    None,
                                    is_diapason,
                                    False
                                )
                            )
                            serch_props_prod_and_add_motrum_props_diapason(
                                vendor_property_and_motrum, supplier_sheets
                            )

                        if type_save == "categ":
                            prod_prop_motrum, prod_prop_value_motrum = (
                                create_motrum_props(
                                    name_motrum, value_motrum, is_diapason
                                )
                            )
                            vendor_property_and_motrum, created = (
                                create_motrum_props_and_vendor(
                                    supplier_sheets,
                                    None,
                                    prod_prop_motrum,
                                    prod_prop_value_motrum,
                                    name_supplier,
                                    value_supplier,
                                    is_diapason,
                                    True
                                )
                            )
                            if category:
                                category_name = category.strip()
                                serch_prod_to_motrum_props_categ(
                                    prod_prop_motrum,
                                    prod_prop_value_motrum,
                                    None,
                                    supplier,
                                    is_diapason,
                                    None,
                                    None,
                                    category_name,
                                )
                                
                                products = Product.objects.filter(
                                    supplier=supplier_sheets,
                                    article_supplier=article_rpl,
                                )
                                if not products:
                                    if article not in not_product:
                                        not_product.append(article)

                        print("-----")
                except Exception as e:
                    print(e)
                    tr = traceback.format_exc()
                    error = "file_error"
                    location = "РАзбор х-к мотрум из фаила (pandas)"
                    info = f"Конкретный товар строка {sheet_name}{idx}{row}{e}{tr}"
                    e = error_alert(error, location, info)
            print(not_product)
    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        error = "file_error"
        location = "РАзбор х-к мотрум из фаила (pandas)"
        info = f"общая{e}{tr}"
        e = error_alert(error, location, info)
