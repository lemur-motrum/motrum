import requests

from apps.core.utils import get_category
from apps.product.models import Product
from apps.supplier.models import Supplier, SupplierCategoryProductAll, Vendor


def iek_api():
    supplier = Supplier.objects.get(slug="iek")
    vendors = Vendor.objects.filter(supplier=supplier)
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

    def get_iek_category(url_service,url_params):
        
        url = "{0}{1}?{2}".format(base_url, url_service, url_params)
        response = requests.request(
            "GET", url, headers=headers, data=payload, allow_redirects=False
        )
        data = response.json()

        for data_item in data:
            category_lower = data_item["group"].lower()
            article_name = data_item["groupId"]
            category_item = SupplierCategoryProductAll.objects.update_or_create(
                name=category_lower,
                article_name=article_name,
                supplier=supplier,
                vendor=vendor_item,
                defaults={article_name: article_name},
                create_defaults={
                    "name": category_lower,
                },
            )

       
        return data
    def get_iek_product(url_service,url_params):
        url = "{0}{1}?{2}".format(base_url, url_service, url_params)
        response = requests.request(
            "GET", url, headers=headers, data=payload, allow_redirects=False
        )
        data = response.json()
        for data_item in data:
            # основная инфа
                article_suppliers = data_item["art"].lower()
                category_lower = data_item["groupId"].lower()
                article = Product.objects.filter(
                    article_supplier=article_suppliers
                ).exists()
                item_category_all = get_category(supplier.id, vendor_item, category_lower)
                item_category = item_category_all[0]
                item_group = item_category_all[1]
                name = data_item["name"]
                # цены
                
                
            
        return data
    
    
    get_iek_category("ddp","TM=ONI")    
    iek = get_iek_product("products","TM=ONI")
    return iek
