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

    supplier = Supplier.objects.get(slug="iek")
    vendors = Vendor.objects.filter(supplier=supplier)
    currency = Currency.objects.get(words_code="RUB")
    vat = Vat.objects.get(name="20")
    # for vendor_items in vendors:
    #     if vendor_items.slug == "oni":
    #         vendor_id = vendor_items.id
    #         vendor_name = vendor_items.slug
    #         vendor_item = vendor_items

   
   
   
    payload = {}
    encoded = base64.b64encode(os.environ.get("IEK_API_TOKEN").encode())
    decoded = encoded.decode()
    

    headers = {
        # 'Authorization': f"Basic {decoded}",
        # 'Authorization': 'Basic NjAwLTIwMjMwNjI2LTE2Mjg0MS0yMTc6Zk4sNUtfaDFrMVk9bTdDLQ==',
      
    }
    
    

    base_url = "https://lk.iek.ru/api/"


    def get_iek_category(url_service, url_params):

            url = "{0}{1}?{2}".format(base_url, url_service, url_params)
            response = requests.request(
                "GET", url,auth=HTTPBasicAuth(os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")), headers=headers, data=payload, allow_redirects=False
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
            "GET", url, auth=HTTPBasicAuth(os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")), headers=headers, data=payload, allow_redirects=False
        )
        
        responset = response_request(response.status_code, "IEK получение товаров")
        if responset:
            data = response.json()
            if data:
                for data_item in data:
                    try:
                    
                        # основная инфа
                        # получение или добавление вендора
                        if data_item["TM"] == None:
                            break
                        else:    
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
                            if  "price" in  data_item:
                                saleprice = data_item["saleprice"]
                                price = data_item["price"]
                                # if saleprice:
                                #     price_supplier = saleprice
                                # else:
                                #     price_supplier = price

                                extra = data_item["extra"]
                                if extra == "Цена по запросу":
                                    extra= True
                                    price_supplier = 0
                                else:
                                    extra= False
                                    price_supplier = price  
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
                          
                                elif  "ImgJpeg" in data_item: 
                                    img_list = data_item["ImgJpeg"]  
                                    add_save_image(img_list)       

                                else:
                                    pass
                                
                                if "IndPacking" in data_item:  
                                    print(data_item["IndPacking"])
                                    if "png_ref" in data_item["IndPacking"][0]:
                                        print(data_item["IndPacking"][0]["png_ref"]  )
                                        img_list = data_item["IndPacking"][0]["png_ref"]  
                                        add_save_image_logistic(img_list)
                                    elif "jpg_ref" in data_item["IndPacking"]:
                                        print(data_item["IndPacking"]["jpg_ref"]  )
                                        img_list = data_item["IndPacking"]["jpg_ref"]  
                                        add_save_image_logistic(img_list) 
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
                            

                            stock_motrum = 0
                            
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
                                    supplier=supplier, article_supplier=article_suppliers
                                )
                                save_update_product_attr(article, supplier, vendor_add[0],None,item_category_all[2],item_category_all[1],item_category_all[0],description, name)
                                
                                
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
                                price_product._change_reason = 'Автоматическое'
                                price_product.save()
                                
                                # update_change_reason(price_product, "Автоматическое")

                            # остатки
                            # остатки
                            param = "шт"
                            lot = None
                            logistic_parametr_quantity = 1
                            if "LogisticParameters" in data_item:
                                i = 0
                                for logistic_param in data_item["LogisticParameters"]:
                                    i+= 1
                                    if i == 1:
                                        param = logistic_param
                                
                                if "individual" in data_item["LogisticParameters"]:
                                    logistic_parametr_quantity = data_item["LogisticParameters"]["individual"]["quantity"]
                                elif "group" in data_item["LogisticParameters"]:
                                    logistic_parametr_quantity = data_item["LogisticParameters"]["group"]["quantity"]
                                elif "transport" in data_item["LogisticParameters"]:
                                    logistic_parametr_quantity = data_item["LogisticParameters"]["transport"]["quantity"]    
                                         
                                if logistic_parametr_quantity == None:
                                       logistic_parametr_quantity = 1     
                                        

                                lot_short_name = data_item["LogisticParameters"][param]["unit"]          
                                lot_quantity = data_item["LogisticParameters"][param]["quantity"] 
                            
                            
                                if  lot_short_name == "шт":
                                    lot_short = "штука"
                                    lot = Lot.objects.get(name_shorts="шт")
                                    lot_complect = int(logistic_parametr_quantity)
                                    stock_supplier = 0
                                    stock_supplier_unit = 0
                                else:
                                    try:
                                        lot = Lot.objects.get(name_shorts=lot_short_name)
                                    except Lot.DoesNotExist:
                                        lot = lot_chek(lot_short_name)
                                            
                                    lot_complect = int(logistic_parametr_quantity)
                                    stock_supplier = 0                       
                                    
                                
                                
                                
                            stock_supplier = get_iek_stock_one(article)
                            stock_prod_stock_supplier = stock_supplier[0] / int(order_multiplicity)
                            if lot:
                                try:
                                    stock_prod = Stock.objects.get(prod=article)
                                
                                except Stock.DoesNotExist:
                                    stock_prod = Stock(
                                        prod=article,
                                        # lot=lot,
                                        # stock_motrum = stock_motrum
                                    )
                                    
                                finally:
                                    stock_prod.lot = lot
                                    stock_prod.stock_supplier = stock_prod_stock_supplier
                                    stock_prod.stock_supplier_unit = stock_supplier[0]
                                    stock_prod.to_order = stock_supplier[1]
                                    stock_prod.lot_complect = lot_complect
                                    stock_prod.order_multiplicity = order_multiplicity
                                    stock_prod.is_one_sale = is_one_sale
                                    stock_prod.data_update = datetime.datetime.now()
                                    stock_prod._change_reason = 'Автоматическое'
                                    stock_prod.save()
                                    
                                    # update_change_reason(stock_prod, "Автоматическое")
            
                    except Exception as e: 
                        print(e)
                        error = "file_api_error"
                        location = "Загрузка фаилов IEK"
                        info = f"ошибка при чтении товара артикул: {article_suppliers}.{traceback.print_exc()} Тип ошибки:{e}"
                        e = error_alert(error, location, info)
                    finally:    
                        continue      

            else:
                error = "file_api_error"
                location = "Загрузка фаилов IEK"
                info = f"ошибка доступа к дата: {article_suppliers}.{traceback.print_exc()} Тип ошибки:{e}"
                e = error_alert(error, location, info)
                # for data_item in data:
                #     try:
                    
                #         # основная инфа
                #         # получение или добавление вендора
                #         if data_item["TM"] == None:
                #             break
                #         else:    
                #             vendor_add = Vendor.objects.get_or_create(
                #                 supplier=supplier,
                #                 name=data_item["TM"],
                #                 defaults={
                #                     "vat_catalog": None,
                #                     "currency_catalog": currency,
                #                 },
                #             )

                #             article_suppliers = data_item["art"]
                #             category = data_item["groupId"]
                    
                #             categ_names = SupplierCategoryProductAll.objects.filter(
                #                 supplier=supplier, article_name=category
                #             )

                #             item_category_all = get_category(
                #                 supplier, vendor_add[0], categ_names[0].name
                #             )

                #             item_category = item_category_all[0]
                #             item_group = item_category_all[1]
                #             item_group_all = item_category_all[2]

                #             name = data_item["name"]
                            
                #             # цены
                #             if  "price" in  data_item:
                #                 saleprice = data_item["saleprice"]
                #                 price = data_item["price"]
                #                 # if saleprice:
                #                 #     price_supplier = saleprice
                #                 # else:
                #                 #     price_supplier = price

                #                 extra = data_item["extra"]
                #                 if extra == "Цена по запросу":
                #                     extra= True
                #                     price_supplier = 0
                #                 else:
                #                     extra= False
                #                     price_supplier = price  
                #             else:
                #                 extra= True
                #                 price_supplier = 0
                            
                #             # ндс    
                #             if "vat" in data_item:
                #                 vat = data_item["vat"]
                #                 vat_catalog = Vat.objects.get(name=vat)

                #                 vat_include = data_item["vat_included"]    
                #             else:
                #                 vat_catalog = Vat.objects.get(name=20)
                #                 vat_include = True
                            
                #             # описание
                #             if "Description" in data_item:
                #                 description_arr = data_item["Description"]
                #                 for desc in description_arr:
                #                     description = desc["desc_ru"]
                #             else:
                #                 description = None
                                
                #             def add_save_image(img_list):
                #                 # img_list = data_item[name]
                #                 for item_image in img_list:
                #                     # item_count = 0
                #                     if len(item_image) > 0:
                #                         # item_count += 1
                #                         img = item_image["file_ref"]["uri"]

                #                         image = ProductImage.objects.create(product=article)
                #                         update_change_reason(image, "Автоматическое")
                #                         image_path = get_file_path_add(image, img)
                #                         p = save_file_product(img, image_path)
                #                         image.photo = image_path
                #                         image.link = img
                #                         image.save()
                #                         update_change_reason(image, "Автоматическое")
                                        
                #             def add_save_image_logistic(img_list):
                                
                              
                #                 img = img_list["uri"]

                #                 image = ProductImage.objects.create(product=article)
                #                 update_change_reason(image, "Автоматическое")
                #                 image_path = get_file_path_add(image, img)
                #                 p = save_file_product(img, image_path)
                #                 image.photo = image_path
                #                 image.link = img
                #                 image.save()
                #                 update_change_reason(image, "Автоматическое")            
                                
                                
                #             def save_image(
                #                 new_product,
                #             ):
                #                 if "ImgPng" in data_item:
                #                     img_list = data_item["ImgPng"]
                #                     add_save_image(img_list)
                          
                #                 elif  "ImgJpeg" in data_item: 
                #                     img_list = data_item["ImgJpeg"]  
                #                     add_save_image(img_list)       

                #                 else:
                #                     pass
                                
                #                 if "IndPacking" in data_item:  
                #                     print(data_item["IndPacking"])
                #                     if "png_ref" in data_item["IndPacking"][0]:
                #                         print(data_item["IndPacking"][0]["png_ref"]  )
                #                         img_list = data_item["IndPacking"][0]["png_ref"]  
                #                         add_save_image_logistic(img_list)
                #                     elif "jpg_ref" in data_item["IndPacking"]:
                #                         print(data_item["IndPacking"]["jpg_ref"]  )
                #                         img_list = data_item["IndPacking"]["jpg_ref"]  
                #                         add_save_image_logistic(img_list) 
                #                     else:
                #                         pass       
                                    

                #             # def saves_doc(
                #             #     item,
                #             #     article,
                #             #     name_str,
                #             #     type_doc
                #             # ):
                #             #     # try:
                #             #     for sertif in item:
                                
                #             #         doc = sertif["file_ref"]["uri"]
                                    
                                
                #             #         document = ProductDocument.objects.create(
                #             #             product=article, type_doc=type_doc
                #             #         )
                #             #         update_change_reason(document, "Автоматическое")

                #             #         document_path = get_file_path_add(document, doc)
                #             #         p = save_file_product(doc, document_path)
                #             #         document.document = document_path
                #             #         document.link = doc
                #             #         document.name = sertif[name_str]
                #             #         document.save()
                #             #         update_change_reason(document, "Автоматическое")
                #             #     # except item.DoesNotExist:
                #             #     #     pass
                #             # def save_all_doc(data_item,article):
                #             #     # saves_doc(
                #             #     #     data_item["Certificates"],
                #             #     #     article,
                #             #     #     "name"
                #             #     # )
                                
                #             #     if "Certificates" in data_item:
                #             #         saves_doc(
                #             #             data_item["Certificates"],
                #             #             article,
                #             #             "name",
                #             #             "Certificates"
                #             #         )
                #             #     if "InstallationProduct" in data_item:
                #             #         saves_doc(
                #             #             data_item["InstallationProduct"],
                #             #             article,
                #             #             "name",
                #             #             "InstallationProduct"
                #             #         )
                #             #     if "DimensionDrawing" in data_item:
                #             #         saves_doc(
                #             #             data_item["DimensionDrawing"],
                #             #             article,
                #             #             "name",
                #             #             "DimensionDrawing"
                #             #         )
                #             #     if "Passport" in data_item:
                #             #         saves_doc(
                #             #             data_item["Passport"],
                #             #             article,
                #             #             "pubName",
                #             #             "Passport"
                #             #         )
                #             #     if "WiringDiagram" in data_item:
                #             #         saves_doc(
                #             #             data_item["WiringDiagram"],
                #             #             article,
                #             #             "name",
                #             #             "WiringDiagram"
                #             #         )
                #             #     if "Models3d" in data_item:
                #             #         saves_doc(
                #             #             data_item["Models3d"],
                #             #             article,
                #             #             "pubName",
                #             #             "Models3d"
                #             #         )
                #             #     if "Brochure" in data_item:
                #             #         saves_doc(
                #             #             data_item["Brochure"],
                #             #             article,
                #             #             "pubName",
                #             #             "Brochure"
                #             #         )


                #             # # остатки
                #             # param = "шт"
                #             # if "LogisticParameters" in data_item:
                                
                #             #     i = 0
                #             #     for logistic_param in data_item["LogisticParameters"]:
                #             #         i+= 1
                #             #         if i == 1:
                #             #             param = logistic_param
                                      
                #             # lot_short_name = data_item["LogisticParameters"][param]["unit"]          
                #             # lot_quantity = data_item["LogisticParameters"][param]["quantity"] 
                #             # if  lot_short_name == "шт":
                #             #        lot_short = "штука"
                #             #        lot = Lot.objects.get(name_shorts="шт")
                #             #        lot_complect = 1
                #             #        stock_supplier = 0
                #             #        stock_supplier_unit = 0
                #             # else:
                #             #     lot = Lot.objects.get(name_shorts=lot_short_name)
                                       
                            
                #             # if "min_ship" in data_item:
                #             #     if data_item["min_ship"] > 1:
                #             #         # lot_short = "набор"
                #             #         lot_short = "штука"
                #             #     else:
                #             #         lot_short = "штука"
                #             # else: 
                #             #     lot_short = "штука"       

                #             # stock_supplier = 0
                #             # lot_complect = 1
                            
                #             # lots = get_lot(lot_short, stock_supplier, lot_complect)
                            
                            
                #             # lot = lots[0]
                #             # stock_supplier_unit = lots[1]
                            

                #             stock_motrum = 0
                            
                #             if "order_multiplicity" in data_item:
                #                 if data_item["order_multiplicity"] > 1:
                #                     order_multiplicity = data_item["order_multiplicity"]
                #                     is_one_sale = False
                #                 else:
                #                     order_multiplicity = 1
                #                     is_one_sale = True
                #             else: 
                #                 order_multiplicity = 1
                #                 is_one_sale = True
                        
                #             # основной товар
                #             print(article_suppliers)
                #             try:
                #                 article = Product.objects.get(
                #                     supplier=supplier, article_supplier=article_suppliers
                #                 )
                #                 save_update_product_attr(article, supplier, vendor_add[0],None,item_category_all[2],item_category_all[1],item_category_all[0],description, name)
                                
                                
                #                 image =  ProductImage.objects.filter(product=article).exists()   
                #                 if image == False:
                #                     save_image(article)
                #                 # documents =  ProductDocument.objects.filter(product=article).exists()   
                #                 # if documents == False:
                #                 #     save_all_doc(data_item,article)
                                    
                #             except Product.DoesNotExist:
                #                 new_article = create_article_motrum(supplier.id)
                #                 article = Product(
                #                         article=new_article,
                #                         supplier=supplier,
                #                         vendor=vendor_add[0],
                #                         article_supplier=article_suppliers,
                #                         name=name,
                #                         description=description,
                #                         category_supplier_all=item_category_all[2],
                #                         group_supplier=item_category_all[1],
                #                         category_supplier=item_category_all[0],
                #                     )
                #                 article.save()
                #                 update_change_reason(article, "Автоматическое")        
                #                 save_image(article)
                #                 # save_all_doc(data_item,article)
                #             # цены товара
                #             print(article)
                #             try:
                #                 price_product = Price.objects.get(prod=article)

                #             except Price.DoesNotExist:
                #                 price_product = Price(prod=article)

                #             finally:
                #                 price_product.currency = currency
                #                 price_product.price_supplier = price_supplier
                #                 price_product.vat = vat_catalog
                #                 price_product.vat_include = vat_include
                #                 price_product.extra_price = extra
                #                 price_product._change_reason = 'Автоматическое'
                #                 price_product.save()
                                
                #                 # update_change_reason(price_product, "Автоматическое")

                #             # остатки
                #             # остатки
                #             param = "шт"
                #             lot = None
                #             logistic_parametr_quantity = 1
                #             if "LogisticParameters" in data_item:
                #                 i = 0
                #                 for logistic_param in data_item["LogisticParameters"]:
                #                     i+= 1
                #                     if i == 1:
                #                         param = logistic_param
                                
                #                 if "individual" in data_item["LogisticParameters"]:
                #                     logistic_parametr_quantity = data_item["LogisticParameters"]["individual"]["quantity"]
                #                 elif "group" in data_item["LogisticParameters"]:
                #                     logistic_parametr_quantity = data_item["LogisticParameters"]["group"]["quantity"]
                #                 elif "transport" in data_item["LogisticParameters"]:
                #                     logistic_parametr_quantity = data_item["LogisticParameters"]["transport"]["quantity"]    
                                         
                #                 if logistic_parametr_quantity == None:
                #                        logistic_parametr_quantity = 1     
                                        

                #                 lot_short_name = data_item["LogisticParameters"][param]["unit"]          
                #                 lot_quantity = data_item["LogisticParameters"][param]["quantity"] 
                            
                            
                #                 if  lot_short_name == "шт":
                #                     lot_short = "штука"
                #                     lot = Lot.objects.get(name_shorts="шт")
                #                     lot_complect = int(logistic_parametr_quantity)
                #                     stock_supplier = 0
                #                     stock_supplier_unit = 0
                #                 else:
                #                     try:
                #                         lot = Lot.objects.get(name_shorts=lot_short_name)
                #                     except Lot.DoesNotExist:
                #                         lot = lot_chek(lot_short_name)
                                            
                #                     lot_complect = int(logistic_parametr_quantity)
                #                     stock_supplier = 0                       
                                    
                                
                                
                                
                #             stock_supplier = get_iek_stock_one(article)
                #             stock_prod_stock_supplier = stock_supplier[0] / int(order_multiplicity)
                #             if lot:
                #                 try:
                #                     stock_prod = Stock.objects.get(prod=article)
                                
                #                 except Stock.DoesNotExist:
                #                     stock_prod = Stock(
                #                         prod=article,
                #                         # lot=lot,
                #                         # stock_motrum = stock_motrum
                #                     )
                                    
                #                 finally:
                #                     stock_prod.lot = lot
                #                     stock_prod.stock_supplier = stock_prod_stock_supplier
                #                     stock_prod.stock_supplier_unit = stock_supplier[0]
                #                     stock_prod.to_order = stock_supplier[1]
                #                     stock_prod.lot_complect = lot_complect
                #                     stock_prod.order_multiplicity = order_multiplicity
                #                     stock_prod.is_one_sale = is_one_sale
                #                     stock_prod.data_update = datetime.datetime.now()
                #                     stock_prod._change_reason = 'Автоматическое'
                #                     stock_prod.save()
                                    
                #                     # update_change_reason(stock_prod, "Автоматическое")
            
                #     except Exception as e: 
                #         print(e)
                #         error = "file_api_error"
                #         location = "Загрузка фаилов IEK"
                #         info = f"ошибка при чтении товара артикул: {article_suppliers}.{traceback.print_exc()} Тип ошибки:{e}"
                #         e = error_alert(error, location, info)
                #     finally:    
                #         continue      
        else:    
            error = "file_api_error"
            location = "Загрузка фаилов IEK"
            info = f"ошибка доступа к ответу: {article_suppliers}.{traceback.print_exc()} Тип ошибки:{e}"
            e = error_alert(error, location, info)
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
    
    # остатки на складах
    def get_iek_stock_one(prod):
        try:
            url_params = f"sku={prod.article_supplier}"
            url_service = "/residues/json/"
            url = "{0}{1}?{2}".format(base_url, url_service, url_params)
            response = requests.request(
                "GET", url, auth=HTTPBasicAuth(os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")), headers=headers, data=payload, allow_redirects=False
            )
            data = response.json()
            
            if data:
                if len(data["shopItems"]) > 0 :
                    for data_item in data["shopItems"]:
                        if data_item["zakaz"] == 1:
                            to_order = True
                        else:
                            to_order = False
                            
                        stock = 0
                        
                        # product = data_item["sku"]
                        
                        for a in data_item["residues"].values():
                            stock += a
                        
                            
                    return (stock,to_order)    
                else:
                    stock = 0
                    to_order = False
                 
                    return (stock,to_order)
            else:
                error = "file_api_error"
                location = "Загрузка фаилов IEK"
                info = f"ошибка при чтении остатков Тип ошибки:if data else Артикул{prod.article_supplier}"
                e = error_alert(error, location, info)
                stock = 0
                to_order = True
                 
                return (stock,to_order)
            
        except Exception as e: 
                print(e)
                error = "file_api_error"
                location = "Загрузка фаилов IEK"
          
                info = f"ошибка при чтении остатков Тип ошибки:{e}{response.text}{response.content}{data} Артикул{prod.article_supplier}"
                e = error_alert(error, location, info)
    
  
        
   
    def get_iek_property(url_service, url_params):
        url = "{0}{1}?{2}".format(base_url, url_service, url_params)
        response = requests.request(
            "GET", url,auth=HTTPBasicAuth(os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")), headers=headers, data=payload, allow_redirects=False
        )
        
        data = response.json()
       
        if  len(data) > 0 :
            print(99999999999)
            for data_item in data:
                print(8888888)
                try:
                    print(777777777777)
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
                    info = f"ошибка при чтении свойств: .{url_params} Тип ошибки:{e}"
                    e = error_alert(error, location, info)
                finally:    
                    continue 
        else: 
            # нет свойств
            pass       
     

    # get_iek_product("products", f"art=MKP12-V-04-40-20-U")
    # get_iek_property("etim",  f"art=MKP12-V-04-40-20-U")
    
    # категории 
    get_iek_category("ddp", None)
    # запись продуктов и пропсовдля каждого по категориям 
    for item_iek_save_categ in iek_save_categ:
        get_iek_product("products", f"groupId={item_iek_save_categ}")
        get_iek_property("etim",  f"groupId={item_iek_save_categ}")
    


  

  

    # остатки на складах отдельная функция
def get_iek_stock():
    encoded = base64.b64encode(os.environ.get("IEK_API_TOKEN").encode())
    decoded = encoded.decode()
    headers = {
        'Authorization': f"Basic {decoded}", 
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
                "GET", url,auth=HTTPBasicAuth(os.environ.get("IEK_API_LOGIN"), os.environ.get("IEK_API_PASSWORD")), headers=headers, data=payload, allow_redirects=False
            )
            data = response.json()
            if data:
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
                    
                else:
                    stock = 0
                    to_order = False
                   
                
              
                try:
                   
                    
                    stock_prod = Stock.objects.get(prod=product_item)
                
                    # stock_prod = Stock.objects.get(prod_id=product_item.article_supplier)
                    stock_prod.stock_supplier = stock
                    stock_prod.to_order = to_order
                    stock_prod.data_update = datetime.datetime.now()
                    stock_prod._change_reason = 'Автоматическое'
                    stock_prod.save()
                    
                except Stock.DoesNotExist:
                    pass
                    
            
            
            
            
    except Exception as e: 
            print(e)
            error = "file_api_error"
            location = "Загрузка фаилов IEK2"
        
            info = f"2ошибка при чтении остатков Тип ошибки:{e}"
            e = error_alert(error, location, info)
