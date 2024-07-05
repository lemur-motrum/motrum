from html import entities
import requests
from simple_history.utils import update_change_reason

from apps import product
from apps.core.models import Currency, Vat
from apps.core.utils import (
    create_article_motrum,
    create_name_file_downloading,
    get_category,
    get_file_path,
    get_file_path_add,
    get_lot,
    get_price_motrum,
    response_request,
    save_file_product,
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
iek_save_categ = [
"20.01.70",
"01.01.01",
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
# "30.04.03",
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
"30.04.03",
]

def iek_api():
    print(len(iek_save_categ))
    # r = SupplierCategoryProductAll.objects.get(article_name= "01.01.01",)
    # print(r)

    supplier = Supplier.objects.get(slug="iek")
    vendors = Vendor.objects.filter(supplier=supplier)
    currency = Currency.objects.get(words_code="RUB")
    vat = Vat.objects.get(name="20")
    for vendor_items in vendors:
        if vendor_items.slug == "oni":
            vendor_id = vendor_items.id
            vendor_name = vendor_items.slug
            vendor_item = vendor_items

   
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
                                    supplier=supplier,
                                    name=vendor_item,
                                    defaults={
                                        "vat_catalog": vat,
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
         
    def get_iek_product(url_service, url_params):
        entity = "&entity=all"
        url = "{0}{1}?{2}{3}".format(base_url, url_service, url_params, entity)
        response = requests.request(
            "GET", url, headers=headers, data=payload, allow_redirects=False
        )
        responset = response_request(response.status_code, "IEK получение товаров")
      
        data = response.json()
        if data == []:
                    error = "file_api_error"
                    location = "Загрузка фаилов IEK"
                    info = f"Пустая категория {url_params}"
                    e = error_alert(error, location, info)
        else:
            for data_item in data:
                try:
                
                    # основная инфа
                    # получение или добавление вендора
                    vendor_add = Vendor.objects.get_or_create(
                        supplier=supplier,
                        name=data_item["TM"],
                        defaults={
                            "vat_catalog": None,
                            "currency_catalog": currency,
                        },
                    )

                    article_suppliers = data_item["art"]
                    category = data_item["groupId"]
                    categ_names = SupplierCategoryProductAll.objects.get(
                        supplier=supplier, article_name=category
                    )

                    item_category_all = get_category(
                        supplier, vendor_add[0], categ_names.name
                    )
                
                    item_category = item_category_all[0]
                    item_group = item_category_all[1]
                    item_group_all = item_category_all[2]

                    name = data_item["name"]
                    
                    # цены
                    if  "price" in  data_item:
                        saleprice = data_item["saleprice"]
                        price = data_item["price"]
                        if saleprice:
                            price_supplier = saleprice
                        else:
                            price_supplier = price

                        extra = data_item["extra"]
                        if extra == "Цена по запросу":
                            extra= True
                            price_supplier = 0
                        else:
                            extra= False   
                    else:
                        extra= True
                        price_supplier = 0
                    
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
                    def save_image(
                        new_product,
                    ):
                        if "ImgJpeg" in data_item:
                            img_list = data_item["ImgJpeg"]
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

                        else:
                            pass

                    # def saves_doc(
                    #     item,
                    #     article,
                    #     name_str,
                    #     type_doc
                    # ):
                    #     # try:
                    #     for sertif in item:
                           
                    #         doc = sertif["file_ref"]["uri"]
                            
                        
                    #         document = ProductDocument.objects.create(
                    #             product=article, type_doc=type_doc
                    #         )
                    #         update_change_reason(document, "Автоматическое")

                    #         document_path = get_file_path_add(document, doc)
                    #         p = save_file_product(doc, document_path)
                    #         document.document = document_path
                    #         document.link = doc
                    #         document.name = sertif[name_str]
                    #         document.save()
                    #         update_change_reason(document, "Автоматическое")
                    #     # except item.DoesNotExist:
                    #     #     pass
                    # def save_all_doc(data_item,article):
                    #     # saves_doc(
                    #     #     data_item["Certificates"],
                    #     #     article,
                    #     #     "name"
                    #     # )
                        
                    #     if "Certificates" in data_item:
                    #         saves_doc(
                    #             data_item["Certificates"],
                    #             article,
                    #             "name",
                    #             "Certificates"
                    #         )
                    #     if "InstallationProduct" in data_item:
                    #         saves_doc(
                    #             data_item["InstallationProduct"],
                    #             article,
                    #             "name",
                    #             "InstallationProduct"
                    #         )
                    #     if "DimensionDrawing" in data_item:
                    #         saves_doc(
                    #             data_item["DimensionDrawing"],
                    #             article,
                    #             "name",
                    #             "DimensionDrawing"
                    #         )
                    #     if "Passport" in data_item:
                    #         saves_doc(
                    #             data_item["Passport"],
                    #             article,
                    #             "pubName",
                    #             "Passport"
                    #         )
                    #     if "WiringDiagram" in data_item:
                    #         saves_doc(
                    #             data_item["WiringDiagram"],
                    #             article,
                    #             "name",
                    #             "WiringDiagram"
                    #         )
                    #     if "Models3d" in data_item:
                    #         saves_doc(
                    #             data_item["Models3d"],
                    #             article,
                    #             "pubName",
                    #             "Models3d"
                    #         )
                    #     if "Brochure" in data_item:
                    #         saves_doc(
                    #             data_item["Brochure"],
                    #             article,
                    #             "pubName",
                    #             "Brochure"
                    #         )


                    # остатки
                    if "min_ship" in data_item:
                        if data_item["min_ship"] > 1:
                            lot_short = "набор"
                        else:
                            lot_short = "штука"
                    else: 
                        lot_short = "штука"       

                    stock_supplier = 0
                    lot_complect = 1
                    lots = get_lot(lot_short, stock_supplier, lot_complect)
                    lot = lots[0]
                    stock_supplier_unit = lots[1]
                   
                    stock_motrum = 0
                
                    # основной товар
                    try:
                        article = Product.objects.get(
                            supplier=supplier, article_supplier=article_suppliers
                        )
                        image =  ProductImage.objects.filter(product=article).exists()   
                        if image == False:
                            save_image(article)
                        # documents =  ProductDocument.objects.filter(product=article).exists()   
                        # if documents == False:
                        #     save_all_doc(data_item,article)
                            
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
                        save_image(article)
                        # save_all_doc(data_item,article)
                    # цены товара
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
                        price_product.save()
                        update_change_reason(price_product, "Автоматическое")

                    # остатки
                    stock_supplier = get_iek_stock_one(article)
             
                    print(stock_supplier[0])
                    
                    try:
                        stock_prod = Stock.objects.get(prod=article)
                        
                    except Stock.DoesNotExist:
                        stock_prod = Stock(
                            prod=article,
                            lot=lot,
                        )
                        
                    finally:
                        stock_prod.stock_supplier = stock_supplier[0]
                        stock_prod.to_order = stock_supplier[1]
                        stock_prod.stock_motrum = stock_motrum
                        stock_prod.save()
                        update_change_reason(stock_prod, "Автоматическое")

                        
                        
                except Exception as e: 
                    print(e)
                    error = "file_api_error"
                    location = "Загрузка фаилов IEK"
                    info = f"ошибка при чтении товара артикул: {article_suppliers}. Тип ошибки:{e}"
                    e = error_alert(error, location, info)
                finally:    
                    continue      
        
    # def get_iek_stock():
    #     products = Product.objects.filter(supplier=supplier, vendor=vendor_items)
    #     print(123123)
    #     prod_article = "sku="
    #     prod_items = ""
    #     for prod_item in products:

    #         str_item = str(prod_item.article_supplier)
    #         prod_article = prod_article + str_item + ","
    #         # prod_item = f"{prod_item}{str_item}"

    #     url_params = prod_article[:-1]

    #     url_service = "/residues"

    #     url = "{0}{1}?{2}".format(base_url, url_service, url_params)
    #     response = requests.request(
    #         "GET", url, headers=headers, data=payload, allow_redirects=False
    #     )
    #     data = response.json()

    #     for data_item in data["shopItems"]:
    #         stock = 0
    #         product = data_item["sku"]
    #         for a in data_item["residues"].values():
    #             stock += a
            
    #         stocks = Stock.objects.filter(prod__article_supplier=product).update(
    #             stock_supplier=stock, stock_supplier_unit=stock
    #         )

    #     return data["shopItems"]

    def get_iek_stock_one(prod):
        try:

            url_params = f"sku={prod.article_supplier}"

            url_service = "/residues"

            url = "{0}{1}?{2}".format(base_url, url_service, url_params)
            response = requests.request(
                "GET", url, headers=headers, data=payload, allow_redirects=False
            )
            data = response.json()
           
            if data["shopItems"] !=[]:
                for data_item in data["shopItems"]:
                    if data_item["zakaz"] == 1:
                        to_order = True
                    else:
                        to_order = False
                            
                    stock = 0
                    product = data_item["sku"]
                    for a in data_item["residues"].values():
                        stock += a
                return (stock,to_order)    
            else:
                stock = 0
                to_order = False
                return (stock,to_order)
            
        except Exception as e: 
                print(e)
                error = "file_api_error"
                location = "Загрузка фаилов IEK"
                info = f"ошибка при чтении остатков Тип ошибки:{e} Артикул{prod.article_supplier}"
                e = error_alert(error, location, info)
         

    def get_iek_property(url_service, url_params):
        url = "{0}{1}?{2}".format(base_url, url_service, url_params)
        response = requests.request(
            "GET", url, headers=headers, data=payload, allow_redirects=False
        )
   
        data = response.json()
        for data_item in data:
            try:
                prod_article = data_item["Code"]
                try: 
                    prod = Product.objects.get(supplier=supplier,article_supplier=prod_article)
                    old_prop = ProductProperty.objects.filter(product=prod).exists()
                    if old_prop == False:
                        for params in data_item["Features"]:
                            pass_item = False
                    
                            name = params["Attribute"]
                            value = params["value"]
                            unit_measure = None
                            names = name.split("_")
                        
                            if  len(names) > 1:
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
                error = "file_api_error"
                location = "Загрузка фаилов IEK"
                info = f"ошибка при чтении свойств: . Тип ошибки:{e}"
                e = error_alert(error, location, info)
            finally:    
                continue 
     

    get_iek_category("ddp", None)
  
    # запись продуктов по категориям 
    for item_iek_save_categ in iek_save_categ:
        get_iek_product("products", f"groupId={item_iek_save_categ}")
        get_iek_property("etim",  f"groupId={item_iek_save_categ}")
    
    # get_iek_property("etim", None)
  

    return [0]
