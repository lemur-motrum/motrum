import os
from pickletools import int4
from django.db import models
import requests
import json
from django.utils.text import slugify
from pytils import translit

from apps.core.models import Currency
from apps.core.utils import (
    create_article_motrum,
    create_name_file_downloading,
    get_category,
    get_file_path,
    get_lot,
    get_price_motrum,
    save_file_product,
)
from apps.product.models import (
    Lot,
    Price,
    Product,
    ProductDocument,
    ProductImage,
    ProductProperty,
    Stock,
)
from apps.supplier.models import Discount, Supplier, SupplierCategoryProductAll, Vendor
from project.settings import MEDIA_ROOT


def prompower_api():

    url = "https://prompower.ru/api/prod/getProducts"
    payload = json.dumps(
        {
            "email": os.environ.get("PROMPOWER_API_EMAIL"),
            "key": os.environ.get("PROMPOWER_API_KEY"),
        }
    )
    headers = {
        "Content-type": "application/json",
        "Cookie": "nuxt-session-id=s%3Anp9ngMJIwPPIJnpKt1Xow9DA50eUD5OQ.IwH2nwSHFODHMKNUx%2FJRYeOVF9phtKXSV6dg6QQebAU",
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    data = response.json()
    prompower = Supplier.objects.get(slug="prompower")
    vendors = Vendor.objects.filter(supplier=prompower)
    for vendors_item in vendors:
        if vendors_item.slug == "prompower":
            vendor_ids = vendors_item.id
            vendor_names = vendors_item.slug
            vendoris = vendors_item

    # получение всех категорий для каталога
    def add_category():
        category_all = []
        for data_item in data:
            category = {
                "name": data_item["category"],
                # "article_name": data_item["tnved"], тнвед это по таможенной жекларации номер где то есть где то нет где на одном товрае одинаковый
                "supplier": prompower.id,
            }
            category_all.append(category)

        unique_category = [
            dict(t) for t in {frozenset(d.items()) for d in category_all}
        ]
        category_all = SupplierCategoryProductAll.objects.filter(supplier=prompower.id)
        for category in unique_category:
            category_lower = category["name"].lower()

            # category_item = SupplierCategoryProductAll.objects.update_or_create(
            #     name=category_lower, article_name=0, supplier=prompower, vendor=vendoris
            # )
            category_item = SupplierCategoryProductAll.objects.update_or_create(
                name=category_lower,
                article_name=0,
                supplier = prompower,
                vendor = vendoris,
                defaults={category_lower: category_lower},
                create_defaults={"name": category_lower,},
            )

    def add_products():
        base_adress = "https://prompower.ru"
        vendor = Vendor.objects.filter(supplier=prompower)
        vat_catalog = 0
        currency = Currency.objects.get(code=643)

        for vendor_item in vendor:
            if vendor_item.slug == "prompower":
                vendor_id = vendor_item.id
                vendor_name = vendor_item.slug
                vendori = vendor_item
                vat_catalog = vendor_item.vat_catalog.name
                vat_catalog_id = vendor_item.vat_catalog
        vat_catalog = int(vat_catalog)

        i = 0
        for data_item in data:
            i += 1
            if i < 20:
                # основная инфа
                article_suppliers = data_item["article"]
                article = Product.objects.filter(
                    article_supplier=article_suppliers
                ).exists()
    
                category_lower = data_item["category"].lower()
            
                item_category = get_category(prompower.id, vendori, category_lower)[0]
                item_group = get_category(prompower.id, vendori, category_lower)[1]

                # цены
                price_supplier_novat = int(data_item["price"])
                # для мотрум добавляем в цену ндс(приходят без ндс)
                price_supplier = price_supplier_novat + (
                    price_supplier_novat / 100 * vat_catalog
                )
                rub_price_supplier = price_supplier
                # скидки
                all_item_group = None 
                price_motrum_all = get_price_motrum(
                    item_category, item_group, vendor_id, rub_price_supplier,all_item_group
                )
                price_motrum = price_motrum_all[0]
                sale =  price_motrum_all[1]

                # остатки
                lot_short = "base"
                stock_supplier = data_item["instock"]
                lot_complect = 1
                lots = get_lot(lot_short, stock_supplier, lot_complect)
                lot = lots[0]

                stock_supplier_unit = lots[1]
                stock_motrum = 0

                name = data_item["title"]
                description = data_item["description"]

                # сохранение изображений
                def save_image(
                    new_product,
                ):
                    img_list = data_item["img"]
                    if len(img_list) > 0:
                        item_count = 0
                        for img_item in img_list:
                            item_count += 1
                            img = img_item
                            type_file = "img"
                            link = base_adress + img_item
                            filetype = ".jpg"
                            filename = create_name_file_downloading(
                                article_suppliers, item_count
                            )
                            image_path = get_file_path(
                                prompower.slug,
                                vendor_name,
                                type_file,
                                article_suppliers,
                                item_count,
                                place="utils",
                            )
                            image_path_all = image_path + "/" + filename + filetype

                            save_file_product(link, image_path, filename, filetype)
                            image_product = ProductImage.objects.create(
                                product=new_product,
                                photo=image_path_all,
                                # file=image_path_all,
                                link=img,
                            )

                # сохранение документов
                def save_document(
                    new_product,
                ):
                    doc_list = data_item["cad"]
                    if len(doc_list) > 0:
                        item_count_doc = 0
                        for doc_item in doc_list:
                            item_count_doc += 1
                            doc = doc_item["filename"]
                            type_file = "document"
                            link = base_adress + "/CAD/" + doc
                            filetype_list = doc.split(".")
                            filetype = "." + filetype_list[1]
                            filename = create_name_file_downloading(
                                article_suppliers, item_count_doc
                            )
                            doc_path = get_file_path(
                                prompower.slug,
                                vendor_name,
                                type_file,
                                article_suppliers,
                                item_count_doc,
                                place="utils",
                            )
                            document_path_all = doc_path + "/" + filename + filetype

                            save_file_product(link, doc_path, filename, filetype)

                            document_product = ProductDocument.objects.create(
                                product=new_product,
                                document=document_path_all,
                                file=document_path_all,
                                link=doc,
                                type_doc="3D-модель"
                            )

                # обновление товара
                if article:

                    # article = Product.objects.get(article_supplier=article_suppliers)
                    print(article)
                    # price_product = Price.objects.filter(prod=article).update(
                    #     rub_price_supplier=rub_price_supplier,
                    #     price_motrum=price_motrum,sale=sale
                    # )
                    # stock_product = Stock.objects.filter(prod=article).update(
                    #     lot=lot,
                    #     stock_supplier=stock_supplier,
                    #     lot_complect=lot_complect,
                    #     stock_supplier_unit=stock_supplier_unit,
                    #     stock_motrum=stock_motrum,
                    # )
                # созданеи товара
                else:

                    new_article = create_article_motrum(prompower.id, vendor_id)

                    new_product = Product.objects.create(
                        article=new_article,
                        supplier=prompower,
                        vendor_id=vendor_id,
                        article_supplier=article_suppliers,
                        category=item_category,
                        group=item_group,
                        name=name,
                        description=description,
                    )
                    price_product = Price.objects.create(
                        prod=new_product,
                        currency=currency,
                        vat=vat_catalog_id,
                        vat_include=False,
                        price_supplier=price_supplier,
                        rub_price_supplier=rub_price_supplier,
                        price_motrum=price_motrum,
                        sale=sale
                    )

                    # Product.objects.filter(id=new_product.id).update(price=price_product)
                    stock_product = Stock.objects.create(
                        prod=new_product,
                        lot=lot,
                        stock_supplier=stock_supplier,
                        lot_complect=lot_complect,
                        stock_supplier_unit=stock_supplier_unit,
                        stock_motrum=stock_motrum,
                    )

                    # Product.objects.filter(id=new_product.id).update(stock=stock_product)
                    save_image(new_product)
                    save_document(new_product)

                    for prop in data_item["props"]:
                        property_product = ProductProperty.objects.create(
                            product=new_product,
                            name=prop["name"],
                            value=prop["value"],
                        )

    add_category()
    add_products()
    return data
