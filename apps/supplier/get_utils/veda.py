import datetime
import os
from apps.core.models import Currency, Vat
from apps.core.utils import create_article_motrum, save_update_product_attr
from apps.logs.utils import error_alert
from apps.product.models import Lot, Price, Product, Stock
from apps.supplier.models import Supplier, Vendor
import requests
from simple_history.utils import update_change_reason

def veda_api():
    supplier = Supplier.objects.get(slug="veda-mc")
    vendors = Vendor.objects.filter(supplier=supplier)
    for vendors_item in vendors:
        if vendors_item.slug == "veda":
            vendor_id = vendors_item.id
            vendor_names = vendors_item.slug
            vendor = vendors_item
            
    currency = Currency.objects.get(words_code="USD")        
     # добавление товаров  
     
    url = "https://driveshub.ru/vedaorder/api/stock_list/6312174204"

    headers = {
    'Authorization': f"{os.environ.get("VEDA_API_TOKEN")}",
    # 'Cookie': 'csrftoken=SGCeKpFZXtWm7YnZm9Bmf5ThpnuJpHFxCGXIbqv5SWD0w1rT7NCI7WoGsDD7rLMA'
    }

    response = requests.request("GET", url, headers=headers,)
    data = response.json()
    print(response)
    i = 0
    for data_item in data['prices']:
     
                
        try:
            print(data_item)
            article_suppliers = data_item["materialCode"]
            name = data_item["description"]
                # цены
            vat_include = True
            vat_catalog = Vat.objects.get(name="20")
            
            price_supplier = float(data_item["salesPrice"])
            if price_supplier == 0:
                pass
            sale_persent = float(data_item["discountPercent"])
            # остатки
            lot = Lot.objects.get(name="штука")
            stock_supplier = data_item["avaliability"]
            lot_complect = 1
            stock_motrum = 0
            
            
            # транзитная инфа
            data_transit = None
            transit_count = None
            transit = data_item["transit"] 
            if transit != []:
                for transit_item in transit:
                    
                    fromisoformat_data_transit_new = datetime.datetime.fromisoformat(transit_item["deliveryDate "])
                    
                   
                    if data_transit != None :
                        fromisoformat_data_transit = datetime.datetime.fromisoformat(data_transit)
                        if fromisoformat_data_transit_new < fromisoformat_data_transit:
                            data_transit = transit_item["deliveryDate "]
                            transit_count = transit_item["count"]
                    else:
                        data_transit = transit_item["deliveryDate "]
                        transit_count = transit_item["count"]
                        
                if data_transit != None:
                    data_transit = datetime.datetime.fromisoformat(data_transit)
                    data_transit = data_transit.date()
                    # print(data_transit.date())
                    # print(type(data_transit))
                    # data_transit = datetime.datetime.strftime(data_transit.date(), '%d.%m.%Y')
                    # print(data_transit)e
            try:
                # если товар есть в бдd
                
                article = Product.objects.get(
                    supplier=supplier,
                    vendor=vendor,
                    article_supplier=article_suppliers,
                )
                
                save_update_product_attr(article, supplier, vendor,None,None,None,None,None, name)
                            
                            
            except Product.DoesNotExist:
                    # если товара нет в бд 
                    new_article = create_article_motrum(supplier.id)
                    article = Product(
                        article=new_article,
                        supplier=supplier,
                        vendor=vendor,
                        article_supplier=article_suppliers,
                        name=name,
                        category_supplier_all=None,
                        group_supplier=None,
                        category_supplier=None,
                    )
                    article.save()
                    update_change_reason(article, "Автоматическое")        
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
                price_product.save()
                update_change_reason(price_product, "Автоматическое")

            # остатки
            try:
                stock_prod = Stock.objects.get(prod=article)
            except Stock.DoesNotExist:
                stock_prod = Stock(
                    prod=article, lot=lot, stock_motrum=stock_motrum
                )
            finally:
                print(transit_count,data_transit)
                stock_prod.transit_count = transit_count
                stock_prod.data_transit = data_transit
                stock_prod.stock_supplier = stock_supplier
                stock_prod.save()
                update_change_reason(stock_prod, "Автоматическое")
                            
            
        except Exception as e: 
            print(e)
            error = "file_api_error"
            location = "Загрузка фаилов Veda MC"
            info = f"ошибка при чтении товара артикул: {data_item["materialCode"]}. Тип ошибки:{e}"
            e = error_alert(error, location, info)
        finally:    
            continue      
        
        уу
               
    return [1]
        
