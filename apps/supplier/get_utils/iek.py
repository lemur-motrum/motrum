from html import entities
import requests

from apps import product
from apps.core.models import Currency, Vat
from apps.core.utils import (
    create_article_motrum,
    create_name_file_downloading,
    get_category,
    get_file_path,
    get_lot,
    get_price_motrum,
    response_request,
    save_file_product,
)
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


def iek_api():
    supplier = Supplier.objects.get(slug="iek")
    vendors = Vendor.objects.filter(supplier=supplier)
    currency = Currency.objects.get(code=643)
    for vendor_items in vendors:
        if vendor_items.slug == "oni":
            vendor_id = vendor_items.id
            vendor_name = vendor_items.slug
            vendor_item = vendor_items

    # def iek_authorization():
    #     "curl -ics --user 600-20230626-162841-217:fN,5K_h1k1Y=m7C- https://lk.iek.ru/api/login/"
    payload = {}
    headers = {
        "Authorization": "Basic NjAwLTIwMjMwNjI2LTE2Mjg0MS0yMTc6Zk4sNUtfaDFrMVk9bTdDLQ=="
    }
    base_url = "https://lk.iek.ru/api/"

    def get_iek_category(url_service, url_params):

        url = "{0}{1}?{2}".format(base_url, url_service, url_params)
        response = requests.request(
            "GET", url, headers=headers, data=payload, allow_redirects=False
        )
        
        responset = response_request(response.status_code,"IEK получение групп")
        if responset:
            data = response.json()

            for data_item in data:
                category_supplier = data_item["kind"]
                group_supplier = data_item["section"]
                category_lower = data_item["group"]
                article_name = data_item["groupId"]
                vendor_item = data_item["TM"]
                vendor_add = Vendor.objects.get_or_create(
                    supplier=supplier,
                    name=vendor_item,
                    defaults={
                        "vat_catalog": None,
                        "currency_catalog": currency,
                    },
                )
                article_name_re = article_name.split(".")

                category_supplier_item = SupplierCategoryProduct.objects.get_or_create(
                    supplier=supplier,
                    name=category_supplier,
                    defaults={
                        "vendor": None,
                        "name": category_supplier,
                        "article_name": article_name_re[0],
                    },
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
                    supplier=supplier,
                    vendor=vendor_add[0],
                    defaults={
                        "article_name": article_name,
                        "vendor": vendor_add[0],
                        "category_supplier": category_supplier_item[0],
                        "group_supplier": groupe_supplier_item[0],
                    },
                )

            return data

    def get_iek_product(url_service, url_params):
        entity = "&entity=all"
        url = "{0}{1}?{2}{3}".format(base_url, url_service, url_params, entity)
        response = requests.request(
            "GET", url, headers=headers, data=payload, allow_redirects=False
        )
        responset = response_request(response.status_code,"IEK получение товаров")
        if responset:
            data = response.json()
            i = 0
            for data_item in data:
                i += 1
                if i < 10:
                    # основная инфа
                    # получение или добавление вендора
                    vendor_add = Vendor.objects.get_or_create(
                    supplier=supplier,
                    name=data_item["TM"],
                    defaults={
                        "vat_catalog": None,
                        "currency_catalog": currency,
                    }, )
                    
                    print(vendor_add[0].name)
                
                    article_suppliers = data_item["art"]
                    article = Product.objects.filter(
                        article_supplier=article_suppliers
                    ).exists()

                    category = data_item["groupId"]
                    categ_names = SupplierCategoryProductAll.objects.get(supplier=supplier,vendor=vendor_add[0],article_name=category)
                    
                    item_category_all = get_category(supplier, vendor_add[0], categ_names.name)
                    item_category = item_category_all[0]
                    item_group = item_category_all[1]
                    item_group_vendor = item_category_all[2]
        
                    # categ_names = SupplierCategoryProductAll.objects.get(supplier=supplier,vendor=vendor_add[0],article_name=category)
                    # all_categ = get_category(supplier, vendor_add[0], categ_names.name)[2]
                    name = data_item["name"]
                    # цены
                    vat = data_item["vat"]
                    vat_catalog = Vat.objects.get(name=vat)

                    vat_include = data_item["vat_included"]
                    saleprice = data_item["saleprice"]
                    extra = data_item["extra"]
                    price = data_item["price"]
                    if saleprice:
                        price_supplier = saleprice
                        # rub_price_supplier = saleprice
                    else:
                        price_supplier = price
                        # rub_price_supplier = price
                    
                    # price_motrum_all = get_price_motrum(
                    #     item_category,
                    #     item_group,
                    #     vendor_id,
                    #     rub_price_supplier,
                    #     item_group_vendor,
                    # )
                    # price_motrum = price_motrum_all[0]
                    # sale = None

                    description_arr = data_item["Description"]
                    for desc in description_arr:
                        description = desc["desc_ru"]

                    def save_image(
                        new_product,
                    ):
                        if "ImgJpeg" in data_item:
                            img_list = data_item["ImgJpeg"]

                            for item_image in img_list:

                                item_count = 0
                                if len(item_image) > 0:
                                    item_count += 1

                                    img = item_image["file_ref"]["uri"]

                                    type_file = "img"
                                    filetype = ".jpg"
                                    filename = create_name_file_downloading(
                                        article_suppliers, item_count
                                    )
                                    image_path = get_file_path(
                                        supplier.slug,
                                        vendor_add[0].name,
                                        type_file,
                                        article_suppliers,
                                        item_count,
                                        place="utils",
                                    )
                                    image_path_all = image_path + "/" + filename + filetype
                                    save_file_product(img, image_path, filename, filetype)
                                    image_product = ProductImage.objects.create(
                                        product=new_product,
                                        photo=image_path_all,
                                        # file=image_path_all,
                                        link=img,
                                    )
                        else:
                            pass

                    def saves_doc(
                        item,
                        article_suppliers,
                        supplier,
                        vendor_name,
                        new_product,
                        name_item,
                    ):
                        try:

                            item_count_doc = 0
                            for sertif in item:
                                item_count_doc += 1

                                # name_item = "_sertificates"
                                type_name = sertif["type"]
                                doc = sertif["file_ref"]["uri"]
                                type_file = "document"
                                filetype = "." + str(sertif["filetype"])

                                type_file = "document"

                                article_name_doc = article_suppliers + name_item
                                filename = create_name_file_downloading(
                                    article_name_doc, item_count_doc
                                )

                                doc_path = get_file_path(
                                    supplier,
                                    vendor_name,
                                    type_file,
                                    article_suppliers,
                                    item_count_doc,
                                    place="utils",
                                )

                                document_path_all = doc_path + "/" + filename + filetype
                                save_file_product(doc, doc_path, filename, filetype)
                                document_product = ProductDocument.objects.create(
                                    product=new_product,
                                    document=document_path_all,
                                    file=document_path_all,
                                    link=doc,
                                    type_doc=type_name,
                                )

                        except item.DoesNotExist:
                            pass

                    def save_doc_img(
                        item,
                        article_suppliers,
                        supplier,
                        vendor_name,
                        new_product,
                        name_item,
                        type_name,
                    ):

                        item_count_doc = 0

                        for sertif in item:

                            item_count_doc += 1

                            # type_name = sertif["type"]
                            doc = sertif["file_ref"]["uri"]
                            type_file = "document"
                            # filetype = "." + str(sertif["filetype"])
                            images_last_list = doc.split(".")
                            filetype = "." + images_last_list[-1]
                            type_file = "document"

                            article_name_doc = article_suppliers + name_item
                            filename = create_name_file_downloading(
                                article_name_doc, item_count_doc
                            )

                            doc_path = get_file_path(
                                supplier,
                                vendor_name,
                                type_file,
                                article_suppliers,
                                item_count_doc,
                                place="utils",
                            )

                            document_path_all = doc_path + "/" + filename + filetype
                            save_file_product(doc, doc_path, filename, filetype)
                            document_product = ProductDocument.objects.create(
                                product=new_product,
                                document=document_path_all,
                                file=document_path_all,
                                link=doc,
                                type_doc=type_name,
                            )

                    # остатки
                    if data_item["min_ship"] > 1:
                        lot_short = "Набор"
                    else:
                        lot_short = "штука"

                    stock_supplier = 0
                    lot_complect = 1
                    lots = get_lot(lot_short, stock_supplier, lot_complect)
                    lot = lots[0]
                    stock_supplier_unit = lots[1]

                    stock_motrum = 0

                    if article:
                     
                        article = Product.objects.get(article_supplier=article_suppliers)
                        
                        price_product = Price.objects.get(prod=article.id)
                        price_product.price_supplier = price_supplier
                        price_product.vat = vat_catalog
                        price_product.vat_include = vat_include
                        price_product.save()
                        
                        stock_supplier = get_iek_stock_one(article)
                        stock_prod=Stock.objects.get(prod=article.id)
                        stock_prod.stock_supplier=stock_supplier
                        stock_prod.stock_motrum=stock_motrum
                        stock_prod.save()
                        # price_product = Price.objects.filter(
                        #     prod=article,
                        # ).update(
                        #     currency=currency,
                        #     vat=vat_catalog,
                        #     vat_include=vat_include,
                        #     price_supplier=price_supplier,
                        #     rub_price_supplier=rub_price_supplier,
                        #     price_motrum=price_motrum,
                        #     sale=sale,
                        # )
                        # get_iek_stock()
                    else:

                        new_article = create_article_motrum(supplier.id, vendor_id)
            
                        new_product = Product.objects.create(
                            article=new_article,
                            supplier=supplier,
                            vendor=vendor_add[0],
                            # vendor_id=vendor_id,
                            article_supplier=article_suppliers,
                            # category_id=item_category.id,
                            # group_id=item_group.id,
                            name=name,
                            description=description,
                            category_supplier_all_id=item_group_vendor.id,
                        )
                        
                        price_product = Price(prod=new_product,price_supplier=price_supplier, currency=currency, vat=vat_catalog,vat_include=vat_include)
                        price_product.save()
                        
                    #     price_product = Price.objects.create(
                    #         prod=new_product,
                    #         currency=currency,
                    #         vat=vat_catalog,
                    #         vat_include=vat_include,
                    #         price_supplier=price_supplier,
                    #         rub_price_supplier=rub_price_supplier,
                    #         price_motrum=price_motrum,
                    #         sale=sale,
                    #     )
                        save_image(new_product)
                        saves_doc(
                            data_item["Certificates"],
                            article_suppliers,
                            supplier,
                            vendor_add[0].name,
                            new_product,
                            "_sertificates",
                        )
                        if "InstallationProduct" in data_item:
                            save_doc_img(
                                data_item["InstallationProduct"],
                                article_suppliers,
                                supplier,
                                vendor_add[0].name,
                                new_product,
                                "_InstallationProduct",
                                "Руководство по монтажу и эксплуатации",
                            )
                        if "DimensionDrawing" in data_item:

                            save_doc_img(
                                data_item["DimensionDrawing"],
                                article_suppliers,
                                supplier,
                                vendor_add[0].name,
                                new_product,
                                "_DimensionDrawing",
                                "Габаритные чертежи",
                            )
                        if "Passport" in data_item:

                            save_doc_img(
                                data_item["Passport"],
                                article_suppliers,
                                supplier,
                                vendor_add[0].name,
                                new_product,
                                "_Passport",
                                "Паспорт",
                            )
                        if "WiringDiagram" in data_item:

                            save_doc_img(
                                data_item["WiringDiagram"],
                                article_suppliers,
                                supplier,
                                vendor_add[0].name,
                                new_product,
                                "_WiringDiagram",
                                "Схема подключения",
                            )
                        if "Models3d" in data_item:

                            save_doc_img(
                                data_item["Models3d"],
                                article_suppliers,
                                supplier,
                                vendor_add[0].name,
                                new_product,
                                "_Models3d",
                                "3D модели",
                            )
                        if "Brochure" in data_item:

                            save_doc_img(
                                data_item["Brochure"],
                                article_suppliers,
                                supplier,
                                vendor_add[0].name,
                                new_product,
                                "_Brochure",
                                "Брошюра",
                            )
                        stock_supplier = get_iek_stock_one(new_product)
                        stock_product = Stock(prod=new_product, lot=lot, stock_supplier=stock_supplier,stock_motrum=stock_motrum,)
                        stock_product.save()
                    #     stock_product = Stock.objects.create(
                    #         prod=new_product,
                    #         lot=lot,
                    #         stock_supplier=stock_supplier,
                    #         lot_complect=lot_complect,
                    #         stock_supplier_unit=stock_supplier_unit,
                    #         stock_motrum=stock_motrum,
                    #     )
                    #     

            return data

    def get_iek_stock():
        products = Product.objects.filter(supplier=supplier, vendor=vendor_items)
        prod_article = "sku="
        prod_items = ""
        for prod_item in products:

            str_item = str(prod_item.article_supplier)
            prod_article = prod_article + str_item + ","
            # prod_item = f"{prod_item}{str_item}"

        url_params = prod_article[:-1]

        url_service = "/residues"

        url = "{0}{1}?{2}".format(base_url, url_service, url_params)
        response = requests.request(
            "GET", url, headers=headers, data=payload, allow_redirects=False
        )
        data = response.json()

        for data_item in data["shopItems"]:
            stock = 0
            product = data_item["sku"]
            for a in data_item["residues"].values():
                stock += a

            stocks = Stock.objects.filter(prod__article_supplier=product).update(
                stock_supplier=stock, stock_supplier_unit=stock
            )

        return data["shopItems"]

    def get_iek_stock_one(prod):
       
        url_params = f"sku={prod.article_supplier}"

        url_service = "/residues"

        url = "{0}{1}?{2}".format(base_url, url_service, url_params)
        response = requests.request(
            "GET", url, headers=headers, data=payload, allow_redirects=False
        )
        data = response.json()

        for data_item in data["shopItems"]:
            stock = 0
            product = data_item["sku"]
            for a in data_item["residues"].values():
                stock += a
                
        return stock

    
    def get_iek_property(url_service, url_params):
        url = "{0}{1}?{2}".format(base_url, url_service, url_params)
        response = requests.request(
            "GET", url, headers=headers, data=payload, allow_redirects=False
        )
        data = response.json()
        for data_item in data:
            prod_article = data_item["Code"]
   
            for params in data_item["Features"]:
                name = params["Attribute"]
                value = params["value"]
                pass_item = False
                if "unit" in params:
                    unit_measure = params["unit"]
                else:
                    names = name.split("_")
              
                    name = names[0]
                    if names[1] == "Code":
                        pass_item = True

                if pass_item == False:
                    try:
                        prod = Product.objects.get(article_supplier=prod_article)
                        ProductProperty.objects.create(
                            product=prod,
                            name=name,
                            value=value,
                            unit_measure=unit_measure,
                        )
                    except Product.DoesNotExist:
                        pass

        return data

    get_iek_category("ddp", None)
    get_iek_product("products", "TM=ONI")
    # # get_iek_property("etim", "TM=ONI")
    # iek = get_iek_property("etim", "TM=ONI")
    
    return [0]
