import datetime
from itertools import count
import os
from bs4 import BeautifulSoup
import openpyxl as openxl
import requests
from simple_history.utils import update_change_reason

from apps.core.models import Currency, Vat
from apps.core.utils import create_article_motrum, get_file_path_add, save_file_product
from apps.product.models import (
    Lot,
    Price,
    Product,
    ProductDocument,
    ProductImage,
    ProductProperty,
    Stock,
)
from apps.supplier.models import (
    Supplier,
    SupplierCategoryProduct,
    SupplierGroupProduct,
    Vendor,
)
from project.settings import BASE_DIR, MEDIA_ROOT, NDS


def pars_instart_xlsx():
    # file_path = "{0}/{1}/{2}/{3}".format(MEDIA_ROOT, "price", "instart",'instar.xlsx')
    file_path = os.path.join(BASE_DIR, "media/price/instart/instar.xlsx")
    print(file_path)
    # media/price/instart/instar.xlsx
    excel_doc = openxl.open(filename=file_path, data_only=True)

    sheetnames = excel_doc.sheetnames
    sheet = excel_doc[sheetnames[0]]

    # базовые параметры
    supplier = Supplier.objects.get(slug="instart")
    vendor = Vendor.objects.get(slug="instart")
    currency = Currency.objects.get(words_code="RUB")
    vat = Vat.objects.get(name=NDS)
    lot_item = Lot.objects.get(name="штука")
    # sheet.max_row + 1)
    for index in range(6, sheet.max_row + 1):
        article_supplier = sheet[f"A{index}"].value
        if article_supplier:
            # категория поставщика поиск создание
            category_okt = None
            groupe_okt = None
            category = sheet[f"B{index}"].value

            if category:
                category_okt = SupplierCategoryProduct.objects.get_or_create(
                    supplier=supplier,
                    vendor=vendor,
                    name=category,
                )
                category_okt = category_okt[0]

                # группа поставщика поиск созданеи
                group = sheet[f"C{index}"].value
                if group:
                    groupe_okt = SupplierGroupProduct.objects.get_or_create(
                        category_supplier=category_okt,
                        vendor=vendor,
                        supplier=supplier,
                        name=group,
                    )
                    groupe_okt = groupe_okt[0]
            print(category_okt, groupe_okt)
            model = sheet[f"D{index}"].value
            name = sheet[f"S{index}"].value
            description = sheet[f"T{index}"].value
            try:
                # поиск по товарам до интеграции
                product = Product.objects.get(
                    vendor=vendor,
                    article_supplier=model,
                    additional_article_supplier=None,
                )
                print("1product", product)
                instart_product_upd(
                    product,
                    supplier=supplier,
                    additional_article_supplier=article_supplier,
                    category_supplier=category_okt,
                    group_supplier=groupe_okt,
                    description=description,
                    name=name,
                )
            except Product.DoesNotExist:
                try:
                    # поиск по товарам после интеграции
                    product = Product.objects.get(
                        supplier=supplier,
                        vendor=vendor,
                        additional_article_supplier=article_supplier,
                    )
                    instart_product_upd(
                        product,
                        supplier=supplier,
                        additional_article_supplier=article_supplier,
                        category_supplier=category_okt,
                        group_supplier=groupe_okt,
                        description=description,
                        name=name,
                    )
                except Product.DoesNotExist:

                    new_article = create_article_motrum(supplier.id)
                    product = Product(
                        article=new_article,
                        supplier=supplier,
                        vendor=vendor,
                        article_supplier=model,
                        additional_article_supplier=article_supplier,
                        name=name,
                        description=description,
                        category_supplier=category_okt,
                        group_supplier=groupe_okt,
                    )
                    product.save()
                    update_change_reason(product, "Автоматическое")

            # прайс для товара
            price_supplier = sheet[f"R{index}"].value
            is_float_price_supplier = is_number_instart(price_supplier)
            if is_float_price_supplier:
                price_supplier = float(price_supplier)
                extra = False
            else:
                price_supplier = None
                extra = True

            try:
                price_product = Price.objects.get(prod=product)

            except Price.DoesNotExist:
                price_product = Price(prod=product)

            finally:
                price_product.currency = currency
                price_product.price_supplier = price_supplier
                price_product.vat = vat
                price_product.vat_include = True
                price_product.extra_price = extra
                price_product._change_reason = "Автоматическое"

                price_product.save()

            # остаток товара
            try:
                stock_prod = Stock.objects.get(prod=product)

            except Stock.DoesNotExist:
                stock_prod = Stock(
                    prod=product,
                    lot=lot_item,
                    lot_complect=1,
                )

            finally:
                stock_prod.data_update = datetime.datetime.now()
                stock_prod._change_reason = "Автоматическое"
                stock_prod.save()

            # картинкки товара
            img_1 = sheet[f"AW{index}"].value
            img_2 = sheet[f"AX{index}"].value
            img_3 = sheet[f"AY{index}"].value
            img_4 = sheet[f"AZ{index}"].value
            img_5 = sheet[f"BA{index}"].value

            image = ProductImage.objects.filter(product=product).exists()
            if image == False:
                save_image_instart(product, img_1, img_2, img_3, img_4, img_5)

            # документы товара
            doc_1 = sheet[f"BC{index}"].value
            doc_2 = sheet[f"BD{index}"].value
            doc_3 = sheet[f"BE{index}"].value
            doc_4 = sheet[f"BF{index}"].value
            doc_5 = sheet[f"BG{index}"].value

            doc = ProductDocument.objects.filter(product=product).exists()
            if doc == False:
                save_document_instart(product, doc_1, "Other", "Каталог")
                save_document_instart(
                    product, doc_2, "InstallationProduct", "Руководство по эксплуатации"
                )
                save_document_instart(product, doc_3, "Passport", "Паспорт")
                save_document_instart(product, doc_4, "Certificates", "Cертификат")
                save_document_instart(product, doc_5, "Models3d", "3d модель")

            # пропсы товара
            ip = sheet[f"X{index}"].value
            ip = ip.split("-")
            ip = ip[1].strip()

            props = {
                "Мощность, кВт(общепромыш-ленный режим (G))": sheet[f"E{index}"].value,
                "Мощность, кВт(насосный режим (P))": sheet[f"F{index}"].value,
                "Входной ток, А(общепромыш-ленный режим (G))": sheet[f"G{index}"].value,
                "Входной ток, А(насосный режим (P))": sheet[f"H{index}"].value,
                "Номинальный выходной ток": sheet[f"I{index}"].value,
                "Напряжение, В": sheet[f"J{index}"].value,
                "Макс.вых-ое напр-ие": sheet[f"K{index}"].value,
                "С встроенными тормозными сопротивлениями": sheet[f"L{index}"].value,
                "фильтр ЭМС": sheet[f"M{index}"].value,
                "Для кабеля. м.": sheet[f"N{index}"].value,
                "Сопротивление, Ом": sheet[f"O{index}"].value,
                "Номинальный ток, А": sheet[f"P{index}"].value,
                "Пиковый ток, А": sheet[f"Q{index}"].value,
                "Комплексная защита двигателя от перегрузки": sheet[f"V{index}"].value,
                "Внутренний байпас": sheet[f"W{index}"].value,
                "Степень защиты (IP)": ip,
                "Поддержка протокола PROFINET IO": sheet[f"Y{index}"].value,
                "Макс. частота на выходе": sheet[f"Z{index}"].value,
                "Поддержка протокола TCP": sheet[f"AA{index}"].value,
                "Поддержка протокола MODBUS": sheet[f"AB{index}"].value,
                "Поддержка протокола PROFIBUS": sheet[f"AC{index}"].value,
                "Количество цифров. входов": sheet[f"AD{index}"].value,
                "Количество аналог. выходов": sheet[f"AE{index}"].value,
                "Количество аналог. входов": sheet[f"AF{index}"].value,
                "Количество цифров. выходов": sheet[f"AG{index}"].value,
                "Количество вход. фаз": sheet[f"AH{index}"].value,
                "Количество выход. фаз": sheet[f"AI{index}"].value,
                "Количество HW-интерфейсов RS-485": sheet[f"AJ{index}"].value,
                "Импульсные входы": sheet[f"AK{index}"].value,
                "Импульсные выходы": sheet[f"AL{index}"].value,
                "Частота сети": sheet[f"AM{index}"].value,
                "Рабочая температура": sheet[f"AN{index}"].value,
                "Cтрана производства": sheet[f"AO{index}"].value,
                "Вес, кг": sheet[f"AP{index}"].value,
                "Длина, м": sheet[f"AQ{index}"].value,
                "Ширина, м": sheet[f"AR{index}"].value,
                "Высота, м": sheet[f"AS{index}"].value,
                "Объем, м3": sheet[f"AT{index}"].value,
            }
            
            save_prop_instart(product,props)

        else:
            pass


def instart_product_upd(product, **kwargs):
    for k, v in kwargs.items():
        setattr(product, k, v)
    product.save()


def is_number_instart(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def save_image_instart(product, *img_link):
    for img in img_link:
        if img != None and img != "#N/A":
            image = ProductImage.objects.create(product=product)
            update_change_reason(image, "Автоматическое")
            image_path = get_file_path_add(image, img)
            p = save_file_product(img, image_path)
            image.photo = image_path
            image.link = img
            image.save()
            update_change_reason(image, "Автоматическое")


def save_document_instart(product, link, type, name):
    if link != None:
        base_dir = "products"
        path_name = "document"
        base_dir_supplier = product.supplier.slug
        base_dir_vendor = product.vendor.slug
        old_doc = ProductDocument.objects.filter(link=link)
        if old_doc.count() > 0:
            old_doc = old_doc[0]
            old_doc.pk = None
            old_doc.product = product
            old_doc.save()
        else:
            document = ProductDocument.objects.create(product=product)
   
            document_path = get_file_path_add(document, link)
            p = save_file_product(link, document_path)
            document.document = document_path
            document.link = link
            document.name = name
            document.save()
            update_change_reason(document, "Автоматическое")
          


def save_prop_instart(product,prop_arr):
    for k, v in prop_arr.items():
        if v != None:
            property_product = ProductProperty(
                product=product,
                name=k,
                value=v,
            )
            property_product.save()
            update_change_reason(property_product, "Автоматическое")
