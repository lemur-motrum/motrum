from itertools import product
import os
import traceback
from apps.core.models import Currency, Vat
from apps.core.utils import create_article_motrum, get_file_path_add, save_file_product, save_update_product_attr
from apps.logs.utils import error_alert
from apps.product.models import (
    Lot,
    Price,
    Product,
    ProductImage,
    ProductProperty,
    Stock,
)
from apps.supplier.get_utils.instart import _save_prop_instart
from apps.supplier.models import (
    Supplier,
    SupplierCategoryProduct,
    SupplierCategoryProductAll,
    SupplierGroupProduct,
    Vendor,
)
import requests
from bs4 import BeautifulSoup
from django.utils.text import slugify
from pytils import translit
import openpyxl as openxl
from project.settings import NDS
from simple_history.utils import update_change_reason
import random
import xlrd


def get_innovert_xml():
    try:
        supplier = Supplier.objects.get(slug="promsiteh")
        urls_xml = os.environ.get("PRST_XML")
        urls_xml_arr = urls_xml.split(", ")
        currency = Currency.objects.get(words_code="RUB")
        vat = Vat.objects.get(name=NDS)
        lot_item = Lot.objects.get(name="штука")

        for url in urls_xml_arr:
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.content, "xml")
                categories = soup.find("categories")
                
                def _category_items_get(category_items_last, vendor):
                        category_supplier = None
                        group_supplier = None
                        category_supplier_all = None

                        category_item_lst = categories.find(
                            "category", {"id": category_items_last}
                        )
                        one_categ_name = category_item_lst.text
                        one_categ_id = category_items_last

                        two_categ_name = None
                        two_categ_id = None

                        three_categ_name = None
                        three_categ_id = None

                        parentId = category_item_lst.get("parentId")
                        if parentId:
                            parrant_elem_one = categories.find(
                                "category", {"id": parentId}
                            )
                            
                            slugish = translit.translify(parrant_elem_one.text)
                            vendor_textslug = slugify(slugish)
                            
                            # Проверяем, является ли родительская категория вендором
                            if vendor is None:
                                vendor = _vengor_get_create_innovert(
                                    parrant_elem_one.text, currency, vat
                                )
                            
                            # Если родительская категория не является вендором
                            if vendor_textslug != vendor.slug:
                                one_categ_name = parrant_elem_one.text
                                one_categ_id = parentId
                                
                                two_categ_name = category_item_lst.text
                                two_categ_id = category_items_last

                                id_par_to_parr_elem = parrant_elem_one.get("parentId")
                                if id_par_to_parr_elem:
                                    parrant_elem_two = categories.find(
                                        "category", {"id": id_par_to_parr_elem}
                                    )

                                    slugish = translit.translify(parrant_elem_two.text)
                                    vendor_textslug = slugify(slugish)
                                    
                                    if vendor is None:
                                        vendor = _vengor_get_create_innovert(
                                            parrant_elem_two.text, currency, vat
                                        )
                                    
                                    if vendor_textslug != vendor.slug:
                                        one_categ_name = parrant_elem_two.text
                                        one_categ_id = id_par_to_parr_elem

                                        two_categ_name = parrant_elem_one.text
                                        two_categ_id = parentId

                                        three_categ_name = category_item_lst.text
                                        three_categ_id = category_items_last

                        if one_categ_id:
                            category_supplier, create = (
                                SupplierCategoryProduct.objects.get_or_create(
                                    supplier=supplier,
                                    vendor=vendor,
                                    name=one_categ_name,
                                    article_name=one_categ_id,
                                )
                            )
                            if two_categ_id:
                                group_supplier, create2 = (
                                    SupplierGroupProduct.objects.get_or_create(
                                        supplier=supplier,
                                        vendor=vendor,
                                        category_supplier=category_supplier,
                                        name=two_categ_name,
                                        article_name=two_categ_id,
                                    )
                                )
                                if three_categ_id:
                                    category_supplier_all, create3 = (
                                        SupplierCategoryProductAll.objects.get_or_create(
                                            supplier=supplier,
                                            vendor=vendor,
                                            category_supplier=category_supplier,
                                            group_supplier=group_supplier,
                                            name=three_categ_name,
                                            article_name=three_categ_id,
                                        )
                                    )

                        return (
                            vendor,
                            category_supplier,
                            group_supplier,
                            category_supplier_all,
                        )

                items = soup.find_all("offer")
                i = 0
                for item in items:
                    i += 1
                    article = item.find("vendorCode")
                    
                    try:
                        if article:
                            article = article.text  # article
                            print("article", article)

                            barcode = None
                            vendor_item = item.find("vendor")  # vendor
                            if vendor_item:
                                vendor_text = vendor_item.text
                                
                                vendor = _vengor_get_create_innovert(
                                    vendor_text, currency, vat
                                )
                            else:
                                vendor = None
                            name = item.find("name").text
                            description = item.find("description").text
                            item_categoryId = item.find("categoryId").text

                            (
                                vendor,
                                category_supplier,
                                group_supplier,
                                category_supplier_all,
                            ) = _category_items_get(item_categoryId, vendor)
                            # ОТКЛЮЧИТЬ ПОИСК ПО ТОВАРАМ ПОСЛЕ ПЕРВОГО ПРОХОДА
                            # поиск по товарам до интеграции
                            try:
                                product = Product.objects.get(
                                    vendor=vendor,
                                    article_supplier=article,
                                )
                                _innovert_product_upd(
                                    product,
                                    supplier=supplier,
                                    category_supplier=category_supplier,
                                    group_supplier=group_supplier,
                                    category_supplier_all=category_supplier_all,
                                    description=description,
                                    name=name,
                                )
                            except Product.DoesNotExist:
                                try:
                                    product = Product.objects.get(
                                        supplier=supplier,
                                        vendor=vendor,
                                        article_supplier=article,
                                    )
                                    save_update_product_attr(
                                            product,
                                            supplier,
                                            vendor,
                                            None,
                                            category_supplier_all,
                                            group_supplier,
                                            category_supplier,
                                            description,
                                            name,
                                        )
                                    # _innovert_product_upd(
                                    #     product,
                                    #     supplier=supplier,
                                    #     vendor=vendor,
                                    #     category_supplier=category_supplier,
                                    #     group_supplier=group_supplier,
                                    #     category_supplier_all=category_supplier_all,
                                    #     description=description,
                                    #     name=name,
                                    # )
                                except Product.DoesNotExist:
                                    new_article = create_article_motrum(supplier.id)
                                    product = Product(
                                        article=new_article,
                                        article_supplier=article,
                                        supplier=supplier,
                                        vendor=vendor,
                                        category_supplier=category_supplier,
                                        group_supplier=group_supplier,
                                        category_supplier_all=category_supplier_all,
                                        description=description,
                                        name=name,
                                    )
                                    product.save()
                                    update_change_reason(product, "Автоматическое")

                            # цены
                            price = item.find("price")
                            if price:
                                price_supplier = price.text
                                price_supplier = float(price_supplier)
                                extra = False
                            else:
                                price_supplier = None
                                extra = True
                            try:
                                price_product = Price.objects.get(prod=product)

                            except Price.DoesNotExist:
                                price_product = Price(prod=product)
                                price_product.currency = currency
                                price_product.vat = vat
                                price_product.vat_include = True
                                
                            finally:
                                price_product.price_supplier = price_supplier
                                price_product.extra_price = extra
                                price_product._change_reason = "Автоматическое"
                                price_product.save()
                                

                            # # картинкки товара
                            # imgs = item.find_all("picture")
                            # image = ProductImage.objects.filter(
                            #     product=product
                            # ).exists()
                            # if image == False and imgs:
                            #     _save_image_innovert(product, imgs)

                            # пропсы товара
                            # props = ProductProperty.objects.filter(
                            #     product=product
                            # ).exists()
                            # if props == False:
                            #     props = item.find_all("param")
                            #     weight = item.find("weight")
                            #     country_of_origin = item.find("country_of_origin")
                            #     _save_prop_innovert(
                            #         product, props, weight, country_of_origin
                            #     )
                            
                            # остатки
                            try:
                                stock_prod = Stock.objects.get(prod=product)
                            except Stock.DoesNotExist:
                                stock_supplier = None

                                stock_prod = Stock(
                                    prod=product,
                                    lot=lot_item,
                                    stock_supplier=stock_supplier,
                                )
                                stock_prod._change_reason = "Автоматическое"
                                stock_prod.save()


                        
                    except Exception as e:
                        print(e)
                        tr = traceback.format_exc()
                        print(tr)
                        error = "file_error"
                        location = "Разбор фаилов innovert конкретный товар "

                        info = f"get_innovert_xml items urls_xml_arr{url}{tr}{e}{article}"
                        e = error_alert(error, location, info)
        
            except Exception as e:
                print(e)
                tr = traceback.format_exc()
                print(tr)
                error = "file_error"
                location = "Разбор фаилов innovert конкретный xml"

                info = f"get_innovert_xml urls_xml_arr{url}{tr}{e}"
                e = error_alert(error, location, info)
    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        print(tr)
        error = "file_error"
        location = "Разбор фаилов innovert"

        info = f"get_innovert_xml{tr}{e}"
        e = error_alert(error, location, info)


def get_innovert_xlsx_stock():
    pass


def _vengor_get_create_innovert(vendor_text, currency, vat):
    slug_text = vendor_text
    slugish = translit.translify(slug_text)
    vendor_textslug = slugify(slugish)
    vendor, created = Vendor.objects.get_or_create(
        slug=vendor_textslug,
        defaults={
            "currency_catalog": currency,
            "vat_catalog": vat,
            "name": vendor_text,
        },
    )
    return vendor


def _innovert_product_upd(product, **kwargs):
    for k, v in kwargs.items():
        setattr(product, k, v)
    product.save()


def _save_image_innovert(product, img_link_arr):
    print(img_link_arr)
    for img in img_link_arr:
        print(img.text)
        image = ProductImage.objects.create(product=product)
        update_change_reason(image, "Автоматическое")
        try:
            image_path = get_file_path_add(image, img.text)
            p = save_file_product(img.text, image_path)
            image.photo = image_path
            image.link = img.text
            image.save()
            update_change_reason(image, "Автоматическое")
        except Exception as e:
            image.delete()


def _save_prop_innovert(product, props, weight, country_of_origin):
    print(props, weight, country_of_origin)
    if weight:
        property_product_weight = ProductProperty(
            product=product,
            name="Вес",
            value=weight.text,
        )
        property_product_weight.save()
        update_change_reason(property_product_weight, "Автоматическое")
    if country_of_origin:
        property_product_country_of_origin = ProductProperty(
            product=product,
            name="Страна",
            value=country_of_origin.text,
        )
        property_product_country_of_origin.save()
        update_change_reason(property_product_country_of_origin, "Автоматическое")

    if props:
        for prop in props:
            parm = prop.get("name")
            value = prop.text
            property_product = ProductProperty(
                product=product,
                name=parm,
                value=value,
            )
            property_product.save()
            update_change_reason(property_product, "Автоматическое")


def save_stock_innovert():
    
    try:
        vat = Vat.objects.get(name=NDS)
        currency = Currency.objects.get(words_code="RUB")
        
        supplier = Supplier.objects.get(slug="promsiteh")
        urls_xls = os.environ.get("PRST_XLS")
        urls_xls_arr = urls_xls.split(", ")
        lot_item = Lot.objects.get(name="штука")
        
        for url in urls_xls_arr:
            response = requests.get(url)
            # Сохраняем временный файл
            temp_file = f"/tmp/innovert_stock_{random.randint(1000, 9999)}.xls"
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            
            try:
                excel_doc = xlrd.open_workbook(temp_file)
                sheet = excel_doc.sheet_by_index(0)
                
                # Получаем названия столбцов из первой строки
                headers = sheet.row_values(0)
                print(headers)
                headers_stock_all = [header for header in headers if str(header) == "Остаток"]
                print(headers_stock_all)
                
                # Получаем индексы из оригинального списка
                column_indices = {header: idx for idx, header in enumerate(headers)}
                # print("Индексы всех столбцов:", column_indices)
                
                # Получаем индексы нужных столбцов
                id_article_column = column_indices.get("Артикул") 
                id_stock_column = column_indices.get("Остаток")
                id_vendor_column = column_indices.get("Параметр: Бренд")
                print("Индекс столбца Артикул:", id_article_column)
                print("Индекс столбца Остаток:", id_stock_column)
                
                for row_idx in range(1, sheet.nrows):
                    row = sheet.row_values(row_idx)
                    try:
                        article = row[id_article_column] if id_article_column is not None else None
                        stock = row[id_stock_column] if id_stock_column is not None else None
                        vendor = row[id_vendor_column] if id_vendor_column is not None else None
                        
                        print(f"Строка {row_idx}:")
                        print(f"Артикул: {article}")
                        print(f"Остаток: {stock}")
                        print(f"Бренд: {vendor}")
                        print("-" * 50)
                        
                        if vendor and article:
                            if stock == 0 or stock == 0.00:
                                stock = 0
                            else:
                                stock = int(stock)
                            
                            try:
                                vendor = _vengor_get_create_innovert(vendor, currency, vat)
                                product = Product.objects.get(
                                            supplier=supplier,
                                            vendor=vendor,
                                            article_supplier=article,
                                        )
                                stock_prod = Stock.objects.get(prod=product)
                                stock_prod.stock_supplier = stock
                                stock_prod.save()
                                
                            except Product.DoesNotExist:
                                print(e)
                                tr = traceback.format_exc()
                                print(tr)
                                error = "file_error"
                                location = f"Такого твоара нет   {row_idx}:{url} {article}{tr}"
                                continue
                        else:
                            error = "file_error"
                            location = f"Разбор фаилов innovert Ошибка в строке {row_idx}{url}{article}{vendor}{stock}"
                            try:
                                product = Product.objects.get(
                                            supplier=supplier,
                                            article_supplier=article,
                                        )
                                stock_prod = Stock.objects.get(prod=product)
                                stock_prod.stock_supplier = stock
                                stock_prod.save()
                            except Exception as e:
                                print(e)
                                tr = traceback.format_exc()
                                print(tr)
                                error = "file_error"
                                location = f"Разбор фаилов innovert Бренд нет  {row_idx}:{url}{e}{tr}"
                                
                    except Exception as e:
                        print(e)
                        tr = traceback.format_exc()
                        print(tr)
                        error = "file_error"
                        location = f"Разбор фаилов innovert Бренд нет  {row_idx}:{url}{e}{tr}"
                        continue
            finally:
                # Удаляем временный файл
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        print(tr)
        error = "file_error"
        location = "Разбор фаилов innovert xls остатки"