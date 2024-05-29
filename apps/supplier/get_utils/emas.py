from datetime import date, timedelta
from genericpath import exists
from mimetypes import init
import os
from tokenize import group
import xml.etree.ElementTree as ET
from xml.etree import ElementTree, ElementInclude
from openpyxl import Workbook
from openpyxl import load_workbook
import openpyxl as openxl
import logging

from apps import product
from apps.core.models import Currency
from apps.core.utils import create_article_motrum, get_category, lot_chek
from apps.logs.utils import error_alert
from apps.product.models import Lot, Price, Product, Stock
from apps.supplier.models import (
    Supplier,
    SupplierCategoryProduct,
    SupplierCategoryProductAll,
    SupplierGroupProduct,
    Vendor,
)
from project.settings import BASE_DIR


def get_emas():
    supplier = Supplier.objects.get(slug="emas")
    vendor = None
    # vendor = Vendor.objects.get(slug="emas")

    def get_emas_categoru():
        # октрываем фаил хмл с копией сайта поставщика
        path = os.path.join(BASE_DIR, "tmp/emas.xml")
        try:
            xml_file = ET.parse(path)
            print(xml_file)
            root = xml_file.getroot()
            ElementInclude.include(root)
            # находить раздел с описанием категорий
            category = root.findall(
                "./Классификатор/Группы/Группа/Ид"
            )  # добавить ошибку невозможно считать путь
            for cat in category:
                category_supplier = cat.text
                category_supplier_name_item = root.findall(
                    f"./Классификатор/Группы/Группа[Ид='{category_supplier}']/Наименование"
                )
                for categ_name in category_supplier_name_item:
                    category_supplier_name = categ_name.text

                sup_categ = SupplierCategoryProduct.objects.update_or_create(
                    supplier=supplier,
                    vendor=vendor,
                    article_name=category_supplier,
                    defaults={"name": category_supplier_name},
                    create_defaults={"name": category_supplier_name},
                )
                category_supplier_item = root.findall(
                    f"./Классификатор/Группы/Группа[Ид='{category_supplier}']/Группы/Группа//"
                )
                # еслие сть вложенная группа
                if category_supplier_item:

                    group_supplier_item = root.findall(
                        f"./Классификатор/Группы/Группа[Ид='{category_supplier}']/Группы/Группа/Ид"
                    )

                    for groupe_item in group_supplier_item:
                        groupe_supplier = groupe_item.text
                        group_supplier_name = root.findall(
                            f"./Классификатор/Группы/Группа[Ид='{category_supplier}']/Группы/Группа/[Ид='{groupe_supplier}']/Наименование"
                        )

                        for group_supplier_name_item in group_supplier_name:
                            group_supplier_name_text = group_supplier_name_item.text

                        groupe_item = SupplierGroupProduct.objects.update_or_create(
                            supplier=supplier,
                            vendor=vendor,
                            article_name=groupe_supplier,
                            category_supplier=sup_categ[0],
                            defaults={"name": group_supplier_name_text},
                            create_defaults={"name": group_supplier_name_text},
                        )

                        groupe_supplier_item = root.findall(
                            f"./Классификатор/Группы/Группа[Ид='{category_supplier}']/Группы/Группа/[Ид='{groupe_supplier}']//"
                        )
                        # если есть вложенная подгруппа
                        if groupe_supplier_item:

                            sub_groupe = root.findall(
                                f"./Классификатор/Группы/Группа[Ид='{category_supplier}']/Группы/Группа/[Ид='{groupe_supplier}']/Группы/Группа/Ид"
                            )
                            for sub_groupe_item in sub_groupe:
                                sub_groupe_item_supplier = sub_groupe_item.text
                                sub_groupe_supplier_name = root.findall(
                                    f"./Классификатор/Группы/Группа[Ид='{category_supplier}']/Группы/Группа/[Ид='{groupe_supplier}']/Группы/Группа/[Ид='{sub_groupe_item_supplier}']/Наименование"
                                )

                                for (
                                    sub_groupe_supplier_names
                                ) in sub_groupe_supplier_name:
                                    sub_group_supplier_name_text = (
                                        sub_groupe_supplier_names.text
                                    )
                              

                                SupplierCategoryProductAll.objects.update_or_create(
                                    supplier=supplier,
                                    vendor=vendor,
                                    article_name=sub_groupe_item_supplier,
                                    category_supplier=sup_categ[0],
                                    group_supplier=groupe_item[0],
                                    defaults={"name": sub_group_supplier_name_text},
                                    create_defaults={
                                        "name": sub_group_supplier_name_text
                                    },
                                )
                               
        except FileNotFoundError:
            pass

    def get_emas_product():

        # vat = vendor.vat_catalog
        vat = None
        currency = Currency.objects.get(words_code="RUB")
        # lot = Lot.objects.get(name_shorts="шт")
        # Разбираем фаил
        file_path = os.path.join(BASE_DIR, "tmp/emas.xlsx")
        excel_doc = openxl.open(filename=file_path, data_only=True)
        sheetnames = excel_doc.sheetnames  # Получение списка листов книги
        sheet = excel_doc[sheetnames[0]]

        first = 0
        # разбираем строки
        for index in range(sheet.min_row, sheet.max_row+1):
            # считываем артикулы после появления записи артикул в первом стобце
            if first == 0:
                if sheet[f"A{index}"].value == "Артикул":
                    first = index

            elif first != 0:
                if sheet[f"B{index}"].value is None and sheet[f"D{index}"].value is None:
                    a = sheet[f"A{index}"].value
                    article_suppliers = sheet[f"A{index}"].value
                    name = sheet[f"C{index}"].value
                    count = sheet[f"F{index}"].value
                    lot_item = sheet[f"E{index}"].value
                    lot = lot_chek(lot_item)

                    try:
                        prod = Product.objects.get(
                            supplier=supplier, article_supplier=article_suppliers
                        )
                        Product.objects.filter(id=prod.id).update(name=name)

                        price = Price.objects.filter(prod=prod).update()
                        
                        stock_prod=Stock.objects.get(prod=prod)
                        stock_prod.stock_supplier=count
                       
                        stock_prod.save()
                        
                    except Product.DoesNotExist:
                        article = create_article_motrum(supplier.id, 0)
                        prod = Product(name=name, supplier=supplier,vendor=vendor,article_supplier=article_suppliers,)
                        prod.save()
                        # prod = Product.objects.create(
                        #     article=article,
                        #     name=name,
                        #     supplier=supplier,
                        #     vendor=vendor,
                        #     article_supplier=article_suppliers,
                        # )
                        # price_product = Price(prod=prod,price_supplier=price_supplier, currency=currency, vat=vat_catalog_id)
                        # price_product.save()
                        price = Price.objects.create(
                            prod=prod,
                            currency=currency,
                            vat=vat,
                            vat_include=True,
                            price_supplier=None,
                            rub_price_supplier=None,
                            price_motrum=None,
                        )
                        stock_prod=Stock(prod=prod, lot=lot,
                        stock_supplier=count,
                        lot_complect=1,stock_motrum=0)
                        stock_prod.save()
                        # stock = Stock.objects.update_or_create(
                #     prod=prod,
                #     defaults={"stock_supplier": count},
                #     create_defaults={
                #         "lot": lot,
                #         "stock_supplier": count,
                #         "lot_complect": 1,
                #         "stock_supplier_unit": count,
                #         "stock_motrum": 0,
                #     },
                # )
                
                else:
                    error = "file structure"
                    location = "Загрузка фаилов Emas"
                    info = f"Ошибка структуры в строке {index}. Фаил не соответствует обрабатываемой структуре фаила-считывание фаила невозможно"
                    e = error_alert(error, location, info)    
        if first == 0:
            error = "file structure"
            location = "Загрузка фаилов Emas"
            info = "Фаил не соответствует обрабатываемой структуре фаила-считывание фаила невозможно"
            e = error_alert(error, location, info)

    def emas_categoru_invent():
        path = os.path.join(BASE_DIR, "tmp/emas.xml")

        xml_file = ET.parse(path)
        root = xml_file.getroot()
        ElementInclude.include(root)

        product = Product.objects.filter(supplier=supplier, vendor=vendor)
        i = 0 
        for product_item in product:
            if i < 150:
                article = product_item.article_supplier
                prod_id = product_item.id
                groupe_item = root.findall(f".//*[Значение='{article}']../../Группы/")
                if groupe_item:
                    groupe = groupe_item[0].text
                    # print(groupe)

                    try:
                        categ_supplier = SupplierCategoryProductAll.objects.get(
                            article_name=groupe
                        )
                        # print(categ_supplier)
                        categ_motrum = get_category(supplier, vendor, categ_supplier)
                        item_category = categ_motrum[0]
                        item_group = categ_motrum[1]
                        # print(item_category)
                        # print(item_group) = 
                        product_item.category_supplier_all = categ_supplier
                        product_item.save()
                        # Product.objects.filter(id=prod_id).update(
                        #     category_supplier_all=categ_supplier.id,
                        #     category=item_category,
                        #     group=item_group,
                        # )
                    except SupplierCategoryProductAll.DoesNotExist:
                        pass
            
            i += 1        

                

    get_emas_categoru()
    get_emas_product()
    emas_categoru_invent()
    
