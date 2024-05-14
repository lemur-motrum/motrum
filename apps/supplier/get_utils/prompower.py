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

            category_item = SupplierCategoryProductAll.objects.update_or_create(
                name=category_lower, article_name=0, supplier=prompower
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
            if i < 10:
                # основная инфа
                article_suppliers = data_item["article"].lower()
                article = Product.objects.filter(
                    article_supplier=article_suppliers
                ).exists()
                print(
                    Product.objects.filter(article_supplier=article_suppliers).exists()
                )
                category_lower = data_item["category"].lower()
                item_category = get_category(prompower.id, category_lower)[0]
                item_group = get_category(prompower.id, category_lower)[1]
                # цены
                price_supplier_novat = int(data_item["price"])
                # для мотрум добавляем в цену ндс(приходят без ндс)
                price_supplier = price_supplier_novat + (
                    price_supplier_novat / 100 * vat_catalog
                )
                rub_price_supplier = price_supplier
                # скидки
                price_motrum = get_price_motrum(
                    item_category, item_group, vendor_id, rub_price_supplier
                )

                # остатки
                lot_short = "base"
                stock_supplier = data_item["instock"]
                lots = get_lot(lot_short, stock_supplier)
                lot = lots[0]
                lot_complect = lots[1]
                stock_supplier_unit = lots[2]
                stock_motrum = 0
                print(lot)

                img_list = data_item["img"]
                item_count = 0
                for img_item in img_list:
                    item_count += 1
                    img = img_item
                    type_file = "img"
                    link = base_adress + img_item

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
                    image_path_all = get_file_path(
                        prompower.slug,
                        vendor_name,
                        type_file,
                        article_suppliers,
                        item_count,
                        place="none",
                    )

                    save_file_product(link, image_path, filename)
                doc_list = data_item["cad"]
                item_count_doc = 0
                for doc_item in doc_list:
                    item_count_doc += 1
                    doc = doc_item
                    type_file = "document"
                    link = base_adress + doc_item

                    filename = create_name_file_downloading(
                        article_suppliers, item_count
                    )
                    doc_path = get_file_path(
                        prompower.slug,
                        vendor_name,
                        type_file,
                        article_suppliers,
                        item_count,
                        place="utils",
                    )
                    doc_path = get_file_path(
                        prompower.slug,
                        vendor_name,
                        type_file,
                        article_suppliers,
                        item_count,
                        place="none",
                    )

                    save_file_product(link, image_path, filename)
                name = data_item["title"]
                description = data_item["description"]
                # get_image_path(filename,supplier,vendor,type_file)

                if article:
                    article = Product.objects.get(article_supplier=article_suppliers)
                    print(123123123)
                    # обновление товара
                    # Product.objects.filter(article_supplier=article).update(
                    #     name=name,
                    # )
                else:
                    pass
                    # созданеи товара
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
                        currency=currency,
                        vat=vat_catalog_id,
                        price_supplier=price_supplier,
                        rub_price_supplier=rub_price_supplier,
                        price_motrum=price_motrum,
                    )

                    Product.objects.filter(id=new_product.id).update(
                        price=price_product
                    )
                    stock_product = Stock.objects.create(
                        lot=lot,
                        stock_supplier=stock_supplier,
                        lot_complect=lot_complect,
                        stock_supplier_unit=stock_supplier_unit,
                        stock_motrum=stock_motrum,
                    )

                    Product.objects.filter(id=new_product.id).update(
                        stock=stock_product
                    )
                    image_product = ProductImage.objects.create(
                        product=new_product,
                        photo=get_file_path,
                        link=img,
                    )

                    for prop in data_item["props"]:
                        property_product = ProductProperty.objects.create(
                            product=new_product,
                            name=prop["name"],
                            value=prop["value"],
                        )
                    document_product = ProductDocument.objects.create(
                        product=new_product,
                        document=get_file_path,
                        link=doc,
                    )

    add_category()
    add_products()
    return data
