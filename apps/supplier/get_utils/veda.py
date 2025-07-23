import datetime
import os
import traceback
from apps.core.models import Currency, Vat
from apps.core.utils import create_article_motrum, save_update_product_attr
from apps.logs.utils import error_alert
from apps.product.models import Lot, Price, Product, Stock
from apps.supplier.models import Supplier, Vendor
import requests
from simple_history.utils import update_change_reason
import re


def veda_api():
    supplier = Supplier.objects.get(slug="veda-mc")
    vendors = Vendor.objects.filter(slug="veda")
    
    for vendors_item in vendors:
        if vendors_item.slug == "veda":
            vendor_id = vendors_item.id
            vendor_names = vendors_item.slug
            vendor = vendors_item

    # currency = Currency.objects.get(words_code="USD")
    currency = Currency.objects.get(words_code="CNY")
    # добавление товаров

    url = "https://driveshub.ru/vedaorder/api/stock_list/6312174204"

    headers = {
        "Authorization": f"{os.environ.get("VEDA_API_TOKEN")}",
        # 'Cookie': 'csrftoken=SGCeKpFZXtWm7YnZm9Bmf5ThpnuJpHFxCGXIbqv5SWD0w1rT7NCI7WoGsDD7rLMA'
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
    )
    data = response.json()

    for data_item in data["prices"]:
        try:
            article_suppliers = data_item["materialCode"]
            name = data_item["description"]
            # цены
            vat_include = True
            vat_catalog = Vat.objects.get(name="20")

            price_supplier = float(data_item["salesPrice"])
            if price_supplier == 0:
                price_supplier = None
            else:
                price_supplier = price_supplier + (price_supplier / 100 * 20)
            
            sale_persent = float(data_item["discountPercent"])
            # остатки
            lot = Lot.objects.get(name="штука")
            stock_supplier = data_item["avaliability"]
            if stock_supplier == "":
                stock_supplier = 0
            lot_complect = 1

            # транзитная инфа
            data_transit = None
            transit_count = None
            transit = data_item["transit"]
            if transit != []:
                for transit_item in transit:

                    fromisoformat_data_transit_new = datetime.datetime.fromisoformat(
                        transit_item["deliveryDate "]
                    )

                    if data_transit != None:
                        fromisoformat_data_transit = datetime.datetime.fromisoformat(
                            data_transit
                        )
                        if fromisoformat_data_transit_new < fromisoformat_data_transit:
                            data_transit = transit_item["deliveryDate "]
                            transit_count = transit_item["count"]
                    else:
                        data_transit = transit_item["deliveryDate "]
                        transit_count = transit_item["count"]

                if data_transit != None:
                    data_transit = datetime.datetime.fromisoformat(data_transit)
                    data_transit = data_transit.date()

            try:
                # если товар есть в бдd

                article = Product.objects.get(
                    supplier=supplier,
                    vendor=vendor,
                    article_supplier=article_suppliers,
                )
                
                save_update_product_attr(
                    article, supplier, vendor, None, None, None, None, None, name
                )

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
                price_product.extra_price = False
                price_product.currency = currency
                price_product.price_supplier = price_supplier
                price_product.vat = vat_catalog
                price_product.vat_include = vat_include
                price_product._change_reason = "Автоматическое"
                price_product.save()
                # update_change_reason(price_product, "Автоматическое")

            # остатки
            try:
                stock_prod = Stock.objects.get(prod=article)
            except Stock.DoesNotExist:
                stock_prod = Stock(
                    prod=article,
                    lot=lot,
                )
            finally:

                stock_prod.transit_count = transit_count
                stock_prod.data_transit = data_transit
                stock_prod.stock_supplier = stock_supplier
                stock_prod.stock_supplier_unit = stock_supplier
                stock_prod.data_update = datetime.datetime.now()
                stock_prod._change_reason = "Автоматическое"
                stock_prod.save()
                # update_change_reason(stock_prod, "Автоматическое")

        except Exception as e:
            print(e)
            tr = traceback.format_exc()
            error = "file_api_error"
            location = "Загрузка api Veda MC"
            info = f"ошибка при чтении товара артикул: {data_item["materialCode"]}. Тип ошибки:{e}{tr}"
            e = error_alert(error, location, info)
        finally:
            continue

def parse_drives_ru_products():
    """
    Парсит товары с drives.ru по артикулу (article_supplier) для товаров с vendor.slug == 'veda'.
    Получает фото (главные и доп), описание и характеристики, сохраняет их в переменные.
    Проверяет совпадение артикула на странице товара.
    """
    from apps.product.models import Product
    from apps.supplier.models import Vendor
    import requests
    from bs4 import BeautifulSoup

    vendor = Vendor.objects.get(slug="veda")
    products = Product.objects.filter(article_supplier="PBC02003")
    results = []
    print(products)
    for product in products:
        type_code = product.article_supplier  # используем артикул напрямую
        if not type_code:
            continue

        search_url = f"https://drives.ru/search/?query={type_code}"
        print(search_url)
        response = requests.get(search_url)
        if response.status_code != 200:
            continue
        soup = BeautifulSoup(response.text, "html.parser")

        found = False
        for item in soup.find_all('div', class_='s-products__item'):
            link_tag = item.find('a', href=True)
            if not link_tag:
                continue
            product_link = link_tag['href']
            if not product_link.startswith('http'):
                product_link = f"https://drives.ru{product_link}"
            print(product_link)
            prod_resp = requests.get(product_link)
            if prod_resp.status_code != 200:
                continue
            prod_soup = BeautifulSoup(prod_resp.text, "html.parser")

            code_div = prod_soup.find('div', class_='product__code')
            page_article = None
            if code_div:
                span = code_div.find('span')
                if span:
                    page_article = span.get_text(strip=True)
            if not page_article or page_article != product.article_supplier:
                continue  # если артикул не совпал, пропускаем

            # --- Парсинг изображений ---
            main_images = []
            for a in prod_soup.find_all('a', class_='p-images__slider-item'):
                href = a.get('href')
                if href:
                    if not href.startswith('http'):
                        href = f"https://drives.ru{href}"
                    main_images.append(href)

            dop_images = []
            for img in prod_soup.find_all('img', class_='p-images__dop-img'):
                src = img.get('data-src') or img.get('src')
                if src:
                    if not src.startswith('http'):
                        src = f"https://drives.ru{src}"
                    dop_images.append(src)
            # --- Конец парсинга изображений ---

            # --- Преобразование маленьких доп. изображений в большие ---
            big_dop_images = []
            for img_url in dop_images:
                big_url = re.sub(r'\.[0-9]+x[0-9]+\.png$', '.970.png', img_url)
                big_dop_images.append(big_url)
            # --- Конец преобразования ---

            description = None
            desc_div = prod_soup.find('div', class_='product-description')
            if desc_div:
                description = desc_div.get_text(strip=True)

            # --- Парсинг характеристик из features-two-val ---
            features = {}
            features_block = prod_soup.find('div', class_=lambda x: x and x.startswith('features'))
            if features_block:
                for block in features_block.find_all('div', class_='features-two-val__block'):
                    name_div = block.find('div', class_='features-two-val__name')
                    value_div = block.find('div', class_='features-two-val__value')
                    if name_div and value_div:
                        name = name_div.get_text(strip=True)
                        value = value_div.get_text(strip=True)
                        features[name] = value
            # --- Конец парсинга характеристик ---

            results.append({
                'product_id': product.id,
                'type_code': type_code,
                'product_link': product_link,
                'main_images': main_images,
                'dop_images': dop_images,
                'big_dop_images': big_dop_images,
                'description': description,
                'features': features,
                'page_article': page_article,
            })
            print(results)
            found = True
            break  # нашли нужный товар, дальше не ищем
        if not found:
            print(f"Товар с артикулом {type_code} не найден на drives.ru")

    return results
