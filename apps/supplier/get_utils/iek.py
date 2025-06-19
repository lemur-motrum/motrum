from ast import Pass
import datetime
from html import entities
from logging import log
import os
import traceback
import requests
from simple_history.utils import update_change_reason
import base64
from requests.auth import HTTPBasicAuth
from apps import product
from apps.core.models import Currency, Vat
from apps.core.utils import (
    create_article_motrum,
    create_name_file_downloading,
    get_category,
    get_etim_prors_iek,
    get_file_path,
    get_file_path_add,
    get_lot,
    lot_chek,
    response_request,
    save_file_product,
    save_update_product_attr,
)
from apps.logs.utils import error_alert
from apps.product.models import (
    CategoryProduct,
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
    SupplierCategoryProductAll,
    SupplierGroupProduct,
    Vendor,
)
from project.settings import IS_PROD

iek_save_categ = [
    "01.01.01",
    "20.01.70",
    "02.01.01",
    "03.01.01",
    "04.01.01",
    "07.01.01",
    "08.01.01",
    "20.01.01",
    "30.01.01",
    "01.02.01",
    "02.02.01",
    "03.02.01",
    "04.02.01",
    "05.02.01",
    "07.02.01",
    "08.02.01",
    "01.03.01",
    "02.03.01",
    "04.03.01",
    "05.03.01",
    "06.03.01",
    "07.03.01",
    "30.03.01",
    "02.04.01",
    "04.04.01",
    "05.04.01",
    "06.04.01",
    "07.04.01",
    "30.04.01",
    "02.05.01",
    "05.05.01",
    "06.05.01",
    "30.05.01",
    "20.06.01",
    "30.06.01",
    "20.07.01",
    "30.07.01",
    "04.10.01",
    "01.01.02",
    "02.01.02",
    "03.01.02",
    "04.01.02",
    "07.01.02",
    "08.01.02",
    "20.01.02",
    "30.01.02",
    "01.02.02",
    "02.02.02",
    "04.02.02",
    "05.02.02",
    "07.02.02",
    "08.02.02",
    "01.03.02",
    "02.03.02",
    "04.03.02",
    "05.03.02",
    "06.03.02",
    "07.03.02",
    "30.03.02",
    "02.04.02",
    "04.04.02",
    "05.04.02",
    "06.04.02",
    "07.04.02",
    "30.04.02",
    "30.05.02",
    "20.06.02",
    "30.06.02",
    "20.07.02",
    "30.07.02",
    "04.10.02",
    "01.01.03",
    "02.01.03",
    "03.01.03",
    "04.01.03",
    "07.01.03",
    "08.01.03",
    "20.01.03",
    "30.01.03",
    "01.02.03",
    "02.02.03",
    "04.02.03",
    "05.02.03",
    "07.02.03",
    "08.02.03",
    "01.03.03",
    "02.03.03",
    "03.03.03",
    "04.03.03",
    "07.03.03",
    "30.03.03",
    "02.04.03",
    "04.04.03",
    "05.04.03",
    "30.04.03",
    "06.05.03",
    "20.06.03",
    "30.06.03",
    "20.07.03",
    "30.07.03",
    "04.10.03",
    "01.01.04",
    "02.01.04",
    "04.01.04",
    "07.01.04",
    "20.01.04",
    "30.01.04",
    "04.02.04",
    "07.02.04",
    "08.02.04",
    "01.03.04",
    "02.03.04",
    "04.03.04",
    "07.03.04",
    "04.04.04",
    "05.04.04",
    "30.04.04",
    "20.06.04",
    "30.07.04",
    "04.10.04",
    "01.01.05",
    "02.01.05",
    "04.01.05",
    "07.01.05",
    "20.01.05",
    "30.01.05",
    "04.02.05",
    "02.03.05",
    "05.04.05",
    "20.05.05",
    "20.06.05",
    "30.07.05",
    "04.10.05",
    "02.01.06",
    "04.01.06",
    "07.01.06",
    "20.01.06",
    "30.01.06",
    "05.04.06",
    "20.05.06",
    "30.07.06",
    "04.10.06",
    "04.01.07",
    "20.01.07",
    "20.05.07",
    "30.07.07",
    "04.10.07",
    "20.01.08",
    "20.05.08",
    "30.07.08",
    "04.10.08",
    "20.01.09",
    "20.05.09",
    "30.07.09",
    "04.10.09",
    "20.01.10",
    "30.07.10",
    "04.10.10",
    "30.07.11",
    "04.01.12",
    "30.02.01",
    "30.02.02",
    "30.02.03",
    "30.02.04",
    "30.02.05",
    "30.02.06",
    "30.02.07",
    "50.01.01",
    "50.01.02",
    "50.01.03",
    "50.01.04",
    "50.01.05",
    "50.02.01",
    "50.02.02",
    "50.02.03",
    "50.02.04",
    "50.03.01",
    "50.03.02",
    "50.04.01",
    "50.05.01",
    "50.05.02",
    "50.06.01",
    "50.07.01",
    "50.07.02",
    "50.08.01",
    "50.09.01",
    "50.09.02",
    "50.10.01",
    "50.10.02",
    "50.11.01",
    "50.12.01",
    "50.13.01",
    "50.14.01",
]


def iek_api():

    supplier = Supplier.objects.get(slug="iek")
    currency = Currency.objects.get(words_code="RUB")
    vat = Vat.objects.get(name="20")

    payload = {}
    encoded = base64.b64encode(os.environ.get("IEK_API_TOKEN").encode())
    decoded = encoded.decode()

    headers = {
        # 'Authorization': f"Basic {decoded}",
        # 'Authorization': 'Basic NjAwLTIwMjMwNjI2LTE2Mjg0MS0yMTc6Zk4sNUtfaDFrMVk9bTdDLQ==',
    }

    base_url = "https://lk.iek.ru/api/"

    def all_categ_iek(url_service, url_params):
        url = "{0}{1}?{2}".format(base_url, url_service, url_params)
        response = requests.request(
            "GET",
            url,
            auth=HTTPBasicAuth(
                os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")
            ),
            headers=headers,
            data=payload,
            allow_redirects=False,
        )
        responset = response_request(response.status_code, "IEK получение групп")
        if responset:
            data = response.json()
            if data == []:
                error = "file_api_error"
                location = "Загрузка фаилов IEK"
                info = f"Пустой каталог групп"
                e = error_alert(error, location, info)
            else:
                for data_item in data:
                    try:

                        category_supplier = data_item["kind"]
                        group_supplier = data_item["section"]
                        category_lower = data_item["group"]
                        article_name = data_item["groupId"]
                        vendor_item = data_item["TM"]
                        print(article_name, category_lower)
                        if vendor_item:
                            vendor_add = Vendor.objects.get_or_create(
                                name=vendor_item,
                                defaults={
                                    "vat_catalog": vat,
                                    "currency_catalog": currency,
                                },
                            )
                        else:
                            vendor_add = [None]
                        article_name_re = article_name.split(".")

                        category_supplier_item = (
                            SupplierCategoryProduct.objects.get_or_create(
                                supplier=supplier,
                                name=category_supplier,
                                defaults={
                                    "vendor": None,
                                    "name": category_supplier,
                                    "article_name": article_name_re[0],
                                },
                            )
                        )

                        groupe_supplier_item = SupplierGroupProduct.objects.get_or_create(
                            category_supplier=category_supplier_item[0],
                            supplier=supplier,
                            name=group_supplier,
                            defaults={
                                "vendor": None,
                                "article_name": f"{article_name_re[0]}.{article_name_re[1]}",
                            },
                        )

                        all_categ = SupplierCategoryProductAll.objects.filter(
                            supplier=supplier, article_name=article_name
                        )

                        if all_categ.count() > 0:
                            for all_cat_item in all_categ:
                                # категории с названиями совпадают- все ок
                                if all_cat_item.name == category_lower and all_cat_item.is_correct == True:
                                    pass
                                # категории с названиями не совпадают 
                                else:

                                    all_cat_item.is_correct = False
                                    all_cat_item.is_need = False
                                    all_cat_item.save()
                                    error = "info_error"
                                    location = "У категори iek изменились параметры"
                                    info = f"У категори iek изменились параметры - она больше не действительна{all_cat_item.article_name}{all_cat_item.name}"
                                    e = error_alert(error, location, info)
                                    sp = SupplierCategoryProductAll.objects.filter(
                                        supplier=supplier,
                                        article_name=article_name,
                                        name=category_lower,
                                    )
                                    if sp:
                                        pass
                                    else:
                                        SupplierCategoryProductAll.objects.create(
                                            name=category_lower,
                                            article_name=article_name,
                                            supplier=supplier,
                                            vendor=vendor_add[0],
                                            category_supplier=category_supplier_item[0],
                                            group_supplier=groupe_supplier_item[0],
                                            is_need=False,
                                        )
                                        error = "info_error"
                                        location = "Новая категория iek"
                                        info = f"Новая категория iek{article_name}{category_lower}"
                                        e = error_alert(error, location, info)

                        else:
                            SupplierCategoryProductAll.objects.create(
                                name=category_lower,
                                article_name=article_name,
                                supplier=supplier,
                                vendor=vendor_add[0],
                                category_supplier=category_supplier_item[0],
                                group_supplier=groupe_supplier_item[0],
                                is_need=False,
                            )
                            error = "info_error"
                            location = "Новая категория iek"
                            info = f"Новая категория iek{article_name}{category_lower}"
                            e = error_alert(error, location, info)

                    except Exception as e:
                        print(e)
                        error = "file_api_error"
                        location = "Загрузка фаилов IEK"
                        info = f"ошибка при чтении групп: {data_item["article_name"]}. Тип ошибки:{e}"
                        e = error_alert(error, location, info)

    def get_iek_category(url_service, url_params):

        url = "{0}{1}?{2}".format(base_url, url_service, url_params)
        response = requests.request(
            "GET",
            url,
            auth=HTTPBasicAuth(
                os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")
            ),
            headers=headers,
            data=payload,
            allow_redirects=False,
        )
        print(response.headers)

        responset = response_request(response.status_code, "IEK получение групп")

        if responset:

            data = response.json()
            if data == []:
                error = "file_api_error"
                location = "Загрузка фаилов IEK"
                info = f"Пустой каталог групп"
                e = error_alert(error, location, info)
            else:
                for data_item in data:
                    try:
                        article_name = data_item["groupId"]
                        if article_name in iek_save_categ:

                            category_supplier = data_item["kind"]
                            group_supplier = data_item["section"]
                            category_lower = data_item["group"]
                            article_name = data_item["groupId"]
                            vendor_item = data_item["TM"]

                            vendor_add = Vendor.objects.get_or_create(
                                # supplier=supplier,
                                name=vendor_item,
                                defaults={
                                    "vat_catalog": vat,
                                    "currency_catalog": currency,
                                },
                            )

                            article_name_re = article_name.split(".")

                            category_supplier_item = (
                                SupplierCategoryProduct.objects.get_or_create(
                                    supplier=supplier,
                                    name=category_supplier,
                                    defaults={
                                        "vendor": None,
                                        "name": category_supplier,
                                        "article_name": article_name_re[0],
                                    },
                                )
                            )

                            groupe_supplier_item = SupplierGroupProduct.objects.get_or_create(
                                category_supplier=category_supplier_item[0],
                                supplier=supplier,
                                name=group_supplier,
                                defaults={
                                    "vendor": None,
                                    "article_name": f"{article_name_re[0]}.{article_name_re[1]}",
                                },
                            )

                            category_item = SupplierCategoryProductAll.objects.update_or_create(
                                name=category_lower,
                                article_name=article_name,
                                supplier=supplier,
                                vendor=vendor_add[0],
                                defaults={
                                    # "article_name": article_name,
                                    "vendor": vendor_add[0],
                                    "category_supplier": category_supplier_item[0],
                                    "group_supplier": groupe_supplier_item[0],
                                },
                            )

                        else:
                            pass
                    except Exception as e:
                        print(e)
                        error = "file_api_error"
                        location = "Загрузка фаилов IEK"
                        info = f"ошибка при чтении групп: {data_item["article_name"]}. Тип ошибки:{e}"
                        e = error_alert(error, location, info)
                    finally:
                        continue

            # return data

    def get_iek_product(url_service, url_params,page):
        pageSize = 500
        
        next_page = True
        page_params = f'&page={page}&pageSize={pageSize}'
        entity = "&entity=all"
        url = "{0}{1}?{2}{3}{4}".format(base_url, url_service, url_params,page_params,entity)
        print("url",url)

        response = requests.request(
            "GET",
            url,
            auth=HTTPBasicAuth(
                os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")
            ),
            headers=headers,
            data=payload,
            allow_redirects=False,
        )
        print(response.status_code)
        responset = response_request(response.status_code, "IEK получение товаров")
        print(responset)
        if responset and response.headers["content-type"].strip().startswith(
            "application/json"
        ):
            data = response.json()
            data_items = data['items']
            if data_items :
                totalPage = data['totalPage']
                print("totalPage",totalPage)
              
                
                if page == totalPage or totalPage == 0:
                    next_page = False
                    print("totalPagenext_page",next_page)
                
                for data_item in data_items:
                    print(data_item)
                 
                    try:

                        # основная инфа
                        # получение или добавление вендора

                        if data_item["TM"] == None:
                            break
                        else:
                            vendor_add = Vendor.objects.get_or_create(
                                # supplier=supplier,
                                name=data_item["TM"],
                                defaults={
                                    "vat_catalog": None,
                                    "currency_catalog": currency,
                                },
                            )

                            article_suppliers = data_item["art"]
                            print("article_suppliers",article_suppliers)
                            category = data_item["groupId"]

                            categ_names = SupplierCategoryProductAll.objects.filter(
                                supplier=supplier, article_name=category
                            )

                            item_category_all = get_category(
                                supplier, vendor_add[0], categ_names[0].name
                            )

                            item_category = item_category_all[0]
                            item_group = item_category_all[1]
                            item_group_all = item_category_all[2]

                            name = data_item["name"]

                        # цены
                        if "price" in data_item:
                            price = data_item["price"]
                            extra = data_item["extra"]
                            if extra == "Цена по запросу":
                                extra = True
                                price_supplier = 0
                            else:
                                extra = False
                                price_supplier = price
                        else:
                            extra = True
                            price_supplier = 0
                            
                        if "PriceIndividualPost" in data_item and data_item["PriceIndividualPost"] != "" and data_item["PriceIndividualPost"] != 0 and data_item["PriceIndividualPost"] != None:
                            pre_price_motrum = data_item["PriceIndividualPost"]
                            pre_price_motrum = round(pre_price_motrum,2)
                        else:
                            pre_price_motrum = None
                            
                        # ндс
                        if "vat" in data_item:
                            vat = data_item["vat"]
                            vat_catalog = Vat.objects.get(name=vat)

                            vat_include = data_item["vat_included"]
                        else:
                            vat_catalog = Vat.objects.get(name=20)
                            vat_include = True

                        # описание
                        if "Description" in data_item:
                            description_arr = data_item["Description"]
                            for desc in description_arr:
                                description = desc["desc_ru"]
                        else:
                            description = None

                        def add_save_image(img_list):
                            # img_list = data_item[name]
                            for item_image in img_list:
                                # item_count = 0
                                if len(item_image) > 0:
                                    # item_count += 1
                                    img = item_image["file_ref"]["uri"]

                                    image = ProductImage.objects.create(product=article)
                                    update_change_reason(image, "Автоматическое")
                                    image_path = get_file_path_add(image, img)
                                    p = save_file_product(img, image_path)
                                    image.photo = image_path
                                    image.link = img
                                    image.save()
                                    update_change_reason(image, "Автоматическое")

                        def add_save_image_logistic(img_list):

                            img = img_list["uri"]

                            image = ProductImage.objects.create(product=article)
                            update_change_reason(image, "Автоматическое")
                            image_path = get_file_path_add(image, img)
                            p = save_file_product(img, image_path)
                            image.photo = image_path
                            image.link = img
                            image.save()
                            update_change_reason(image, "Автоматическое")

                        def save_image(
                            new_product,
                        ):
                            if "ImgPng" in data_item:
                                img_list = data_item["ImgPng"]
                                add_save_image(img_list)

                            elif "ImgJpeg" in data_item:
                                img_list = data_item["ImgJpeg"]
                                add_save_image(img_list)

                            else:
                                pass

                            if "IndPacking" in data_item:
                                print(data_item["IndPacking"])
                                if "png_ref" in data_item["IndPacking"][0]:
                                    print(data_item["IndPacking"][0]["png_ref"])
                                    img_list = data_item["IndPacking"][0]["png_ref"]
                                    add_save_image_logistic(img_list)
                                elif "jpg_ref" in data_item["IndPacking"]:
                                    print(data_item["IndPacking"]["jpg_ref"])
                                    img_list = data_item["IndPacking"]["jpg_ref"]
                                    add_save_image_logistic(img_list)
                                else:
                                    pass
                        def save_props_etim(
                            new_product,article
                        ):
                            if "ArtEtim" in data_item :
                                prop_list = data_item["ArtEtim"]
                                get_etim_prors_iek(prop_list,article)
                            
                        def saves_doc(item, article, name_str, type_doc):
                            for sertif in item:

                                doc = sertif["file_ref"]["uri"]
                                print(doc)
                                document_bd = ProductDocument.objects.filter(
                                    type_doc=type_doc, link=doc
                                )

                                document = ProductDocument.objects.create(
                                    product=article, type_doc=type_doc
                                )
                                update_change_reason(document, "Автоматическое")
                                if document_bd.count() > 0:
                                    print("old_doc")
                                    document_bd = document_bd[0]
                                    document.document = document_bd.document
                                    document.link = doc
                                    document.name = sertif[name_str]
                                    document.save()
                                    update_change_reason(document, "Автоматическое")
                                else:
                                    print("new_doc")
                                    document_path = get_file_path_add(document, doc)
                                    p = save_file_product(doc, document_path)
                                    document.document = document_path
                                    document.link = doc
                                    document.name = sertif[name_str]
                                    document.save()
                                    update_change_reason(document, "Автоматическое")

                        def save_all_doc(data_item, article):

                            if "Certificates" in data_item:
                                saves_doc(
                                    data_item["Certificates"],
                                    article,
                                    "name",
                                    "Certificates",
                                )
                            if "InstallationProduct" in data_item:
                                saves_doc(
                                    data_item["InstallationProduct"],
                                    article,
                                    "name",
                                    "InstallationProduct",
                                )
                            if "DimensionDrawing" in data_item:
                                saves_doc(
                                    data_item["DimensionDrawing"],
                                    article,
                                    "name",
                                    "DimensionDrawing",
                                )
                            if "Passport" in data_item:
                                saves_doc(
                                    data_item["Passport"],
                                    article,
                                    "pubName",
                                    "Passport",
                                )
                            if "WiringDiagram" in data_item:
                                saves_doc(
                                    data_item["WiringDiagram"],
                                    article,
                                    "name",
                                    "WiringDiagram",
                                )
                            if "Models3d" in data_item:
                                saves_doc(
                                    data_item["Models3d"],
                                    article,
                                    "pubName",
                                    "Models3d",
                                )
                            if "Brochure" in data_item:
                                saves_doc(
                                    data_item["Brochure"],
                                    article,
                                    "pubName",
                                    "Brochure",
                                )

                            # # остатки
                            # param = "шт"
                            # if "LogisticParameters" in data_item:

                            #     i = 0
                            #     for logistic_param in data_item["LogisticParameters"]:
                            #         i+= 1
                            #         if i == 1:
                            #             param = logistic_param

                            # lot_short_name = data_item["LogisticParameters"][param]["unit"]
                            # lot_quantity = data_item["LogisticParameters"][param]["quantity"]
                            # if  lot_short_name == "шт":
                            #        lot_short = "штука"
                            #        lot = Lot.objects.get(name_shorts="шт")
                            #        lot_complect = 1
                            #        stock_supplier = 0
                            #        stock_supplier_unit = 0
                            # else:
                            #     lot = Lot.objects.get(name_shorts=lot_short_name)

                            # if "min_ship" in data_item:
                            #     if data_item["min_ship"] > 1:
                            #         # lot_short = "набор"
                            #         lot_short = "штука"
                            #     else:
                            #         lot_short = "штука"
                            # else:
                            #     lot_short = "штука"

                            # stock_supplier = 0
                            # lot_complect = 1

                            # lots = get_lot(lot_short, stock_supplier, lot_complect)

                            # lot = lots[0]
                            # stock_supplier_unit = lots[1]

                        if "order_multiplicity" in data_item:
                            if data_item["order_multiplicity"] > 1:
                                order_multiplicity = data_item["order_multiplicity"]
                                is_one_sale = False
                            else:
                                order_multiplicity = 1
                                is_one_sale = True
                        else:
                            order_multiplicity = 1
                            is_one_sale = True

                        # основной товар
                        print(article_suppliers)
                        try:
                            article = Product.objects.get(
                                supplier=supplier,
                                article_supplier=article_suppliers,
                                vendor=vendor_add[0],
                            )
                            save_update_product_attr(
                                article,
                                supplier,
                                vendor_add[0],
                                None,
                                item_category_all[2],
                                item_category_all[1],
                                item_category_all[0],
                                description,
                                name,
                            )

                            if IS_PROD:
                                image = ProductImage.objects.filter(
                                    product=article
                                ).exists()
                                if image == False:
                                    save_image(article)

                                documents = ProductDocument.objects.filter(
                                    product=article
                                ).exists()
                                if documents == False:
                                    save_all_doc(data_item, article)
                            
                            props = ProductProperty.objects.filter(
                                    product=article
                                ).exists()
                            if props == False:
                                save_props_etim(data_item, article)

                        except Product.DoesNotExist:
                            new_article = create_article_motrum(supplier.id)
                            article = Product(
                                article=new_article,
                                supplier=supplier,
                                vendor=vendor_add[0],
                                article_supplier=article_suppliers,
                                name=name,
                                description=description,
                                category_supplier_all=item_category_all[2],
                                group_supplier=item_category_all[1],
                                category_supplier=item_category_all[0],
                            )
                            article.save()
                            update_change_reason(article, "Автоматическое")

                            if IS_PROD:
                                save_image(article)
                                save_all_doc(data_item, article)
                                save_props_etim(data_item, article)

                        # цены товара
                        print(article)
                        try:
                            price_product = Price.objects.get(prod=article)

                        except Price.DoesNotExist:
                            price_product = Price(prod=article)

                        finally:
                            price_product.currency = currency
                            price_product.price_supplier = price_supplier
                            price_product.vat = vat_catalog
                            price_product.vat_include = vat_include
                            price_product.extra_price = extra
                            price_product._change_reason = "Автоматическое"
                            price_product.price_motrum = pre_price_motrum
                            price_product.save(force_price_motrum=True)

                            # update_change_reason(price_product, "Автоматическое")

                        # остатки

                        param = "шт"
                        lot = None
                        logistic_parametr_quantity = 1
                        if "LogisticParameters" in data_item:
                            i = 0
                            for logistic_param in data_item["LogisticParameters"]:
                                i += 1
                                if i == 1:
                                    param = logistic_param

                            if "individual" in data_item["LogisticParameters"]:
                                logistic_parametr_quantity = data_item[
                                    "LogisticParameters"
                                ]["individual"]["quantity"]
                            elif "group" in data_item["LogisticParameters"]:
                                logistic_parametr_quantity = data_item[
                                    "LogisticParameters"
                                ]["group"]["quantity"]
                            elif "transport" in data_item["LogisticParameters"]:
                                logistic_parametr_quantity = data_item[
                                    "LogisticParameters"
                                ]["transport"]["quantity"]

                            if logistic_parametr_quantity == None:
                                logistic_parametr_quantity = 1

                            lot_short_name = data_item["LogisticParameters"][param][
                                "unit"
                            ]
                            lot_quantity = data_item["LogisticParameters"][param][
                                "quantity"
                            ]

                            if lot_short_name == "шт":
                                lot_short = "штука"
                                lot = Lot.objects.get(name_shorts="шт")
                                lot_complect = int(logistic_parametr_quantity)
                                stock_supplier = 0
                                stock_supplier_unit = 0
                            else:
                                lot = lot_chek(lot_short_name)
                                # try:
                                #     lot = Lot.objects.get(name_shorts=lot_short_name)
                                # except Lot.DoesNotExist:
                                #     lot = lot_chek(lot_short_name)

                                lot_complect = int(logistic_parametr_quantity)
                                stock_supplier = 0

                        stock, to_order, is_none_error = get_iek_stock_one(
                            article
                        )  # (stock,to_order,is_none_error)
                        print("stock",stock)
                        if is_none_error == False:
                            stock = 0

                        if lot:
                            print("if lot true")
                            if stock != 0:
                                stock_prod_stock_supplier = stock / int(
                                    order_multiplicity
                                )
                            else:
                                stock_prod_stock_supplier = 0
                            print("stock_prod_stock_supplier",stock_prod_stock_supplier)
                            try:
                                stock_prod = Stock.objects.get(prod=article)

                            except Stock.DoesNotExist:
                                stock_prod = Stock(
                                    prod=article,
                                )

                            finally:
                                stock_prod.lot = lot
                                stock_prod.stock_supplier = int(
                                    stock_prod_stock_supplier
                                )
                                stock_prod.stock_supplier_unit = stock
                                stock_prod.to_order = to_order
                                stock_prod.lot_complect = lot_complect
                                stock_prod.order_multiplicity = order_multiplicity
                                stock_prod.is_one_sale = is_one_sale
                                stock_prod._change_reason = "Автоматическое"
                                stock_prod.data_update = datetime.datetime.now()
                                print("THIS @ save")
                                stock_prod.save(force_stock_supplier_unit=True)
                                

                            
                            
                    except Exception as e:
                        print(e)
                        error = "file_api_error"
                        location = "Загрузка фаилов IEK"
                        info = f"ошибка при чтении товара артикул: {article_suppliers}.{traceback.print_exc()} Тип ошибки:{e}"
                        e = error_alert(error, location, info)
                    finally:
                        continue
                return next_page
            else:
                # пустая группа
                return False
                
        else:
            # Не открылся жсон
            return False
            # error = "file_api_error"
            # location = "Загрузка фаилов IEK"
            # info = f"ошибка доступа к ответу {url_params}{responset}{response}"
            # e = error_alert(error, location, info)

    # остатки на складах
    def get_iek_stock_one(prod):
        try:
            url_params = f"sku={prod.article_supplier}"
            url_service = "/residues/json/"
            url = "{0}{1}?{2}".format(base_url, url_service, url_params)
            response = requests.request(
                "GET",
                url,
                auth=HTTPBasicAuth(
                    os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")
                ),
                headers=headers,
                data=payload,
                allow_redirects=False,
            )

            responset = response_request(response.status_code, "IEK получение товаров")

            if responset and response.headers["content-type"].strip().startswith(
                "application/json"
            ):
                try:
                    data = response.json()

                    if data:
                        if len(data["shopItems"]) > 0:
                            for data_item in data["shopItems"]:
                                if data_item["zakaz"] == 1:
                                    to_order = True
                                    error = "file_api_error"
                                    location = "Загрузка фаилов IEK"
                                    info = f"[zakaz] == 1{prod.article_supplier}"
                                    e = error_alert(error, location, info)

                                else:
                                    to_order = False

                                stock = 0
                                for a in data_item["residues"].values():
                                    stock += a
                            is_none_error = True
                            return (stock, to_order, is_none_error)
                        else:
                            stock = None
                            to_order = False
                            is_none_error = False
                            return (stock, to_order, is_none_error)
                    else:
                        stock = None
                        to_order = False
                        is_none_error = False
                        return (stock, to_order, is_none_error)
                except Exception as e:
                    tr = traceback.format_exc()
                    error = "file_api_error"
                    location = "Загрузка фаилов IEK"

                    info = f"ошибка при чтении остатков3333 Тип ошибки:{e}Артикул{prod.article_supplier}{tr}"
                    e = error_alert(error, location, info)
                    stock = None
                    to_order = False
                    is_none_error = False
                    return (stock, to_order, is_none_error)
            else:
                stock = None
                to_order = False
                is_none_error = False
                return (stock, to_order, is_none_error)

        except Exception as e:

            tr = traceback.format_exc()
            error = "file_api_error"
            location = "Загрузка фаилов IEK"
            info = f"ошибка при чтении остатков Тип ошибки:{e}{response.text}{response.content} Артикул{prod.article_supplier}{tr}"
            e = error_alert(error, location, info)
            stock = None
            to_order = False
            is_none_error = False
            return (stock, to_order, is_none_error)

    def get_iek_property(url_service, url_params):
        url = "{0}{1}?{2}".format(base_url, url_service, url_params)
        response = requests.request(
            "GET",
            url,
            auth=HTTPBasicAuth(
                os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")
            ),
            headers=headers,
            data=payload,
            allow_redirects=False,
        )

        data = response.json()

        if len(data) > 0:
            for data_item in data:
                try:
                    prod_article = data_item["Code"]
                    prod_tm = data_item["TM"]
                    prod_tm = prod_tm.lower()
                    try:
                        prod = Product.objects.get(
                            supplier=supplier,vendor__slug=prod_tm, article_supplier=prod_article
                        )
                        old_prop = ProductProperty.objects.filter(product=prod).exists()
                        if old_prop == False:
                            for params in data_item["Features"]:
                                pass_item = False

                                name = params["Attribute"]
                                value = params["value"]
                                unit_measure = None
                                names = name.split("_")

                                if len(names) > 1:
                                    name = names[0]
                                    if names[1] == "Code":
                                        pass_item = True

                                if "unit" in params:
                                    unit_measure = params["unit"]

                                if pass_item == False:

                                    prop = ProductProperty(
                                        product=prod,
                                        name=name,
                                        value=value,
                                        hide=False,
                                        unit_measure=unit_measure,
                                    )

                                    prop.save()
                                    update_change_reason(prop, "Автоматическое")
                    except Product.DoesNotExist:
                        pass
                except Exception as e:
                    print(e)
                    tr = traceback.format_exc()
                    error = "file_api_error"
                    location = "Загрузка фаилов IEK"
                    info = (
                        f"ошибка при чтении свойств: .{url_params} Тип ошибки:{e}{tr}"
                    )
                    e = error_alert(error, location, info)
                finally:
                    continue
        else:
            # нет свойств
            pass
    
    #TODO! вернуть !!!!
    all_categ_iek("ddp", None)
    true_categ = SupplierCategoryProductAll.objects.filter(
                            supplier=supplier,is_correct = True,is_need = True
                        )
    # next_page = get_iek_product("products", f"groupId=30.04.02",1)
    if true_categ.count() > 0:
        for true_cat in true_categ:
            print("TRUECATEG",true_cat.article_name)
            
            page = 0
            next_page = True
            while next_page :
                page += 1
                print(page)
                print(next_page)
                next_page = get_iek_product("products", f"groupId={true_cat.article_name}",page)
                print(next_page)
            
            
            # get_iek_property("etim", f"groupId={true_cat.article_name}")


# остатки на складах отдельная функция
def get_iek_stock():
    encoded = base64.b64encode(os.environ.get("IEK_API_TOKEN").encode())
    decoded = encoded.decode()
    headers = {
        "Authorization": f"Basic {decoded}",
    }
    payload = {}
    base_url = "https://lk.iek.ru/api/"

    try:
        supplier = Supplier.objects.get(slug="iek")
        product = Product.objects.filter(supplier=supplier)
        for product_item in product:

            url_params = f"sku={product_item.article_supplier}"

            url_service = "/residues/json/"

            url = "{0}{1}?{2}".format(base_url, url_service, url_params)
            response = requests.request(
                "GET",
                url,
                auth=HTTPBasicAuth(
                    os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")
                ),
                headers=headers,
                data=payload,
                allow_redirects=False,
            )
            data = response.json()
            if data and data != []:
                if len(data["shopItems"]) > 0:
                    for data_item in data["shopItems"]:
                        if data_item["zakaz"] == 1:
                            to_order = True
                        else:
                            to_order = False

                        stock = 0
                        product = data_item["sku"]
                        for a in data_item["residues"].values():
                            stock += a

                else:
                    stock = 0
                    to_order = False

                try:
                    stock_prod = Stock.objects.get(prod=product_item)
                    if stock != 0:
                        stock_prod_stock_supplier = stock / int(
                            stock_prod.order_multiplicity
                        )
                    else:
                        stock_prod_stock_supplier = 0

                    # stock_prod = Stock.objects.get(prod_id=product_item.article_supplier)
                    stock_prod.stock_supplier = stock_prod_stock_supplier
                    stock_prod.stock_supplier_unit = stock
                    stock_prod.to_order = to_order
                    stock_prod.data_update = datetime.datetime.now()
                    stock_prod._change_reason = "Автоматическое"
                    print("TIS NOW SEVE")
                    stock_prod.save(force_stock_supplier_unit=True)

                except Stock.DoesNotExist:
                    pass
            else:
                pass
    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        error = "file_api_error"
        location = "Загрузка остатки на складах отдельная функция IEK2"

        info = f"2ошибка при чтении остатков Тип ошибки:{e}{tr}"
        e = error_alert(error, location, info)


def update_prod_iek_in_okt():
    encoded = base64.b64encode(os.environ.get("IEK_API_TOKEN").encode())
    decoded = encoded.decode()
    headers = {
        "Authorization": f"Basic {decoded}",
    }
    payload = {}
    base_url = "https://lk.iek.ru/api/"
    supplier = Supplier.objects.get(slug="iek")

    try:
        products = Product.objects.filter(supplier=supplier)
        for product in products:
            
            url_params = f"art={product.article_supplier}"
            print(url_params)
            url_service = "products"

            url = "{0}{1}?{2}".format(base_url, url_service, url_params)
            print("url", url)
            response = requests.request(
                "GET",
                url,
                auth=HTTPBasicAuth(
                    os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")
                ),
                headers=headers,
                data=payload,
                allow_redirects=False,
            )
            data = response.json()
            for data_item in data:
                if data != []:
                    # цены
                    if "price" in data_item:
                        price = data_item["price"]
                        extra = data_item["extra"]
                        if extra == "Цена по запросу":
                            extra = True
                            price_supplier = 0
                        else:
                            extra = False
                            price_supplier = price
                        
                        price_product = Price.objects.get(prod=product)
                        price_product.price_supplier = price_supplier
                        price_product.extra_price = extra
                        price_product._change_reason = "Автоматическое"
                        price_product.save(force_price_motrum=True)
                    else:
                        pass
                        # extra = True
                        # price_supplier = 0

                    # price_product = Price.objects.get(prod=product)
                    # price_product.price_supplier = price_supplier
                    # price_product.extra_price = extra
                    # price_product._change_reason = "Автоматическое"
                    # price_product.save(force_price_motrum=True)

    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        error = "file_api_error"
        location = "Загрузка товаров отдельно от групп IEK2"

        info = f"Загрузка товаров отдельно от групп IEK2 Тип ошибки:{e}{tr}"
        e = error_alert(error, location, info)


def update_prod_iek_get_okt():
    encoded = base64.b64encode(os.environ.get("IEK_API_TOKEN").encode())
    decoded = encoded.decode()
    headers = {
        "Authorization": f"Basic {decoded}",
    }
    payload = {}
    base_url = "https://lk.iek.ru/api/"
    supplier = Supplier.objects.get(slug="iek")
    currency = Currency.objects.get(words_code="RUB")
    vat = Vat.objects.get(name="20")
    try:
        products = Product.objects.filter(supplier=supplier)
        
        for product in products:
            print(product)
            vendor = product.vendor
            url_params = f"art={product.article_supplier}&entity=all"
            print(url_params)
            url_service = "products"

            url = "{0}{1}?{2}".format(base_url, url_service, url_params)
            print("url", url)
            response = requests.request(
                "GET",
                url,
                auth=HTTPBasicAuth(
                    os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")
                ),
                headers=headers,
                data=payload,
                allow_redirects=False,
            )
            data = response.json()
            print(data)
            if data and data != []:
                for data_item in data:
                    article = product
                    category = data_item["groupId"]
                    categ_names = SupplierCategoryProductAll.objects.filter(
                                supplier=supplier, article_name=category
                            )

                    item_category_all = get_category(
                        supplier, vendor, categ_names[0].name
                    )

                    item_category = item_category_all[0]
                    item_group = item_category_all[1]
                    item_group_all = item_category_all[2]
                    
                    name = data_item["name"]
                    if "Description" in data_item:
                            description_arr = data_item["Description"]
                            for desc in description_arr:
                                description = desc["desc_ru"]
                    else:
                        description = None
                    
                # цены
                    if "price" in data_item:
                        price = data_item["price"]
                        extra = data_item["extra"]
                        if extra == "Цена по запросу":
                            extra = True
                            price_supplier = 0
                        else:
                            extra = False
                            price_supplier = price
                    else:
                        extra = True
                        price_supplier = 0
                    if "PriceIndividualPost" in data_item and data_item["PriceIndividualPost"] != "" and data_item["PriceIndividualPost"] != 0 and data_item["PriceIndividualPost"] != None:
                        pre_price_motrum = data_item["PriceIndividualPost"]
                        pre_price_motrum = round(pre_price_motrum,2)
                    # ндс
                    if "vat" in data_item:
                        vat = data_item["vat"]
                        vat_catalog = Vat.objects.get(name=vat)

                        vat_include = data_item["vat_included"]
                    else:
                        vat_catalog = Vat.objects.get(name=20)
                        vat_include = True
                    
                    def add_save_image(img_list):
                        # img_list = data_item[name]
                        for item_image in img_list:
                            # item_count = 0
                            if len(item_image) > 0:
                                # item_count += 1
                                img = item_image["file_ref"]["uri"]

                                image = ProductImage.objects.create(product=article)
                                update_change_reason(image, "Автоматическое")
                                image_path = get_file_path_add(image, img)
                                p = save_file_product(img, image_path)
                                image.photo = image_path
                                image.link = img
                                image.save()
                                update_change_reason(image, "Автоматическое")

                    def add_save_image_logistic(img_list):

                        img = img_list["uri"]

                        image = ProductImage.objects.create(product=article)
                        update_change_reason(image, "Автоматическое")
                        image_path = get_file_path_add(image, img)
                        p = save_file_product(img, image_path)
                        image.photo = image_path
                        image.link = img
                        image.save()
                        update_change_reason(image, "Автоматическое")

                    def save_image(
                        new_product,
                    ):
                        if "ImgPng" in data_item:
                            img_list = data_item["ImgPng"]
                            add_save_image(img_list)

                        elif "ImgJpeg" in data_item:
                            img_list = data_item["ImgJpeg"]
                            add_save_image(img_list)

                        else:
                            pass

                        if "IndPacking" in data_item:
                            print(data_item["IndPacking"])
                            if "png_ref" in data_item["IndPacking"][0]:
                                print(data_item["IndPacking"][0]["png_ref"])
                                img_list = data_item["IndPacking"][0]["png_ref"]
                                add_save_image_logistic(img_list)
                            elif "jpg_ref" in data_item["IndPacking"]:
                                print(data_item["IndPacking"]["jpg_ref"])
                                img_list = data_item["IndPacking"]["jpg_ref"]
                                add_save_image_logistic(img_list)
                            else:
                                pass
                    def save_props_etim(
                        new_product,article
                    ):
                        if "ArtEtim" in data_item :
                            prop_list = data_item["ArtEtim"]
                            get_etim_prors_iek(prop_list,article)
                        
                    def saves_doc(item, article, name_str, type_doc):
                        for sertif in item:

                            doc = sertif["file_ref"]["uri"]
                            print(doc)
                            document_bd = ProductDocument.objects.filter(
                                type_doc=type_doc, link=doc
                            )

                            document = ProductDocument.objects.create(
                                product=article, type_doc=type_doc
                            )
                            update_change_reason(document, "Автоматическое")
                            if document_bd.count() > 0:
                                print("old_doc")
                                document_bd = document_bd[0]
                                document.document = document_bd.document
                                document.link = doc
                                document.name = sertif[name_str]
                                document.save()
                                update_change_reason(document, "Автоматическое")
                            else:
                                print("new_doc")
                                document_path = get_file_path_add(document, doc)
                                p = save_file_product(doc, document_path)
                                document.document = document_path
                                document.link = doc
                                document.name = sertif[name_str]
                                document.save()
                                update_change_reason(document, "Автоматическое")

                    def save_all_doc(data_item, article):

                        if "Certificates" in data_item:
                            saves_doc(
                                data_item["Certificates"],
                                article,
                                "name",
                                "Certificates",
                            )
                        if "InstallationProduct" in data_item:
                            saves_doc(
                                data_item["InstallationProduct"],
                                article,
                                "name",
                                "InstallationProduct",
                            )
                        if "DimensionDrawing" in data_item:
                            saves_doc(
                                data_item["DimensionDrawing"],
                                article,
                                "name",
                                "DimensionDrawing",
                            )
                        if "Passport" in data_item:
                            saves_doc(
                                data_item["Passport"],
                                article,
                                "pubName",
                                "Passport",
                            )
                        if "WiringDiagram" in data_item:
                            saves_doc(
                                data_item["WiringDiagram"],
                                article,
                                "name",
                                "WiringDiagram",
                            )
                        if "Models3d" in data_item:
                            saves_doc(
                                data_item["Models3d"],
                                article,
                                "pubName",
                                "Models3d",
                            )
                        if "Brochure" in data_item:
                            saves_doc(
                                data_item["Brochure"],
                                article,
                                "pubName",
                                "Brochure",
                            ) 
                    
                    
                    
                    save_update_product_attr(
                                product,
                                None,
                                None,
                                None,
                                item_category_all[2],
                                item_category_all[1],
                                item_category_all[0],
                                description,
                                name,
                            )
                    if IS_PROD:
                        image = ProductImage.objects.filter(
                            product=product
                        ).exists()
                        if image == False:
                            save_image(product)

                        documents = ProductDocument.objects.filter(
                            product=product
                        ).exists()
                        if documents == False:
                            save_all_doc(data_item, product)
                    
                    props = ProductProperty.objects.filter(
                            product=product
                        ).exists()
                    if props == False:
                        save_props_etim(data_item, product)
                        
                    try:
                        price_product = Price.objects.get(prod=article)

                    except Price.DoesNotExist:
                        price_product = Price(prod=article)

                    finally:
                        price_product.currency = currency
                        price_product.price_supplier = price_supplier
                        price_product.vat = vat_catalog
                        price_product.vat_include = vat_include
                        price_product.extra_price = extra
                        price_product._change_reason = "Автоматическое"
                        price_product.price_motrum = pre_price_motrum
                        price_product.save(force_price_motrum=True)
                    
                    # остатки
                    # остатки на складах
                    def get_iek_stock_one(prod):
                        try:
                            url_params = f"sku={prod.article_supplier}"
                            url_service = "/residues/json/"
                            url = "{0}{1}?{2}".format(base_url, url_service, url_params)
                            response = requests.request(
                                "GET",
                                url,
                                auth=HTTPBasicAuth(
                                    os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")
                                ),
                                headers=headers,
                                data=payload,
                                allow_redirects=False,
                            )

                            responset = response_request(response.status_code, "IEK получение товаров")

                            if responset and response.headers["content-type"].strip().startswith(
                                "application/json"
                            ):
                                try:
                                    data = response.json()

                                    if data:
                                        if len(data["shopItems"]) > 0:
                                            for data_item in data["shopItems"]:
                                                if data_item["zakaz"] == 1:
                                                    to_order = True
                                                    error = "file_api_error"
                                                    location = "Загрузка фаилов IEK"
                                                    info = f"[zakaz] == 1{prod.article_supplier}"
                                                    e = error_alert(error, location, info)

                                                else:
                                                    to_order = False

                                                stock = 0
                                                for a in data_item["residues"].values():
                                                    stock += a
                                            is_none_error = True
                                            return (stock, to_order, is_none_error)
                                        else:
                                            stock = None
                                            to_order = False
                                            is_none_error = False
                                            return (stock, to_order, is_none_error)
                                    else:
                                        stock = None
                                        to_order = False
                                        is_none_error = False
                                        return (stock, to_order, is_none_error)
                                except Exception as e:
                                    tr = traceback.format_exc()
                                    error = "file_api_error"
                                    location = "Загрузка фаилов IEK"

                                    info = f"ошибка при чтении остатков3333 Тип ошибки:{e}Артикул{prod.article_supplier}{tr}"
                                    e = error_alert(error, location, info)
                                    stock = None
                                    to_order = False
                                    is_none_error = False
                                    return (stock, to_order, is_none_error)
                            else:
                                stock = None
                                to_order = False
                                is_none_error = False
                                return (stock, to_order, is_none_error)

                        except Exception as e:

                            tr = traceback.format_exc()
                            error = "file_api_error"
                            location = "Загрузка фаилов IEK"
                            info = f"ошибка при чтении остатков Тип ошибки:{e}{response.text}{response.content} Артикул{prod.article_supplier}{tr}"
                            e = error_alert(error, location, info)
                            stock = None
                            to_order = False
                            is_none_error = False
                            return (stock, to_order, is_none_error)

                    param = "шт"
                    lot = None
                    logistic_parametr_quantity = 1
                    if "LogisticParameters" in data_item:
                        i = 0
                        for logistic_param in data_item["LogisticParameters"]:
                            i += 1
                            if i == 1:
                                param = logistic_param

                        if "individual" in data_item["LogisticParameters"]:
                            logistic_parametr_quantity = data_item[
                                "LogisticParameters"
                            ]["individual"]["quantity"]
                        elif "group" in data_item["LogisticParameters"]:
                            logistic_parametr_quantity = data_item[
                                "LogisticParameters"
                            ]["group"]["quantity"]
                        elif "transport" in data_item["LogisticParameters"]:
                            logistic_parametr_quantity = data_item[
                                "LogisticParameters"
                            ]["transport"]["quantity"]

                        if logistic_parametr_quantity == None:
                            logistic_parametr_quantity = 1

                        lot_short_name = data_item["LogisticParameters"][param][
                            "unit"
                        ]
                        lot_quantity = data_item["LogisticParameters"][param][
                            "quantity"
                        ]

                        if lot_short_name == "шт":
                            lot_short = "штука"
                            lot = Lot.objects.get(name_shorts="шт")
                            lot_complect = int(logistic_parametr_quantity)
                            stock_supplier = 0
                            stock_supplier_unit = 0
                        else:
                            lot = lot_chek(lot_short_name)
                            # try:
                            #     lot = Lot.objects.get(name_shorts=lot_short_name)
                            # except Lot.DoesNotExist:
                            #     lot = lot_chek(lot_short_name)

                            lot_complect = int(logistic_parametr_quantity)
                            stock_supplier = 0

                    stock, to_order, is_none_error = get_iek_stock_one(
                        article
                    )  # (stock,to_order,is_none_error)

                    if is_none_error == False:
                        stock = 0
                    if "order_multiplicity" in data_item:
                            if data_item["order_multiplicity"] > 1:
                                order_multiplicity = data_item["order_multiplicity"]
                                is_one_sale = False
                            else:
                                order_multiplicity = 1
                                is_one_sale = True
                    else:
                        order_multiplicity = 1
                        is_one_sale = True
                    if lot:
                        print("if lot true")
                        if stock != 0:
                            stock_prod_stock_supplier = stock / int(
                                order_multiplicity
                            )
                        else:
                            stock_prod_stock_supplier = 0

                        try:
                            stock_prod = Stock.objects.get(prod=article)

                        except Stock.DoesNotExist:
                            stock_prod = Stock(
                                prod=article,
                            )

                        finally:
                            stock_prod.lot = lot
                            stock_prod.stock_supplier = int(
                                stock_prod_stock_supplier
                            )
                            stock_prod.stock_supplier_unit = stock
                            stock_prod.to_order = to_order
                            stock_prod.lot_complect = lot_complect
                            stock_prod.order_multiplicity = order_multiplicity
                            stock_prod.is_one_sale = is_one_sale
                            stock_prod._change_reason = "Автоматическое"
                            stock_prod.data_update = datetime.datetime.now()
                            print("NOW SAVE")
                            stock_prod.save(force_stock_supplier_unit=True)
            elif data == []:
                error = "info_error"
                location = "Обновление товаров IEK"

                info = f"Обновление товаров IEK- такого товара нет в API IEK.Возможно его сняли с производства.Уточните информацию и если необходимо снимите товар с доступности {product.article_supplier}"
                e = error_alert(error, location, info)   
                # проометка проверить товар на доступность
                
    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        error = "file_api_error"
        location = "Загрузка товаров отдельно от групп IEK3"

        info = f"Загрузка товаров отдельно от групп IEK3 Тип ошибки:{e}{tr}"
        e = error_alert(error, location, info)