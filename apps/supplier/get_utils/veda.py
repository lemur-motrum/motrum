import datetime
import os
import traceback
from apps.core.models import Currency, Vat
from apps.core.utils import create_article_motrum, save_update_product_attr
from apps.logs.utils import error_alert
from apps.product.models import Lot, Price, Product, Stock
from apps.supplier.models import (
    Supplier,
    SupplierCategoryProduct,
    SupplierGroupProduct,
    Vendor,
)
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

    supplier = Supplier.objects.get(slug="veda-mc")
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
        for item in soup.find_all("div", class_="s-products__item"):
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue
            product_link = link_tag["href"]
            if not product_link.startswith("http"):
                product_link = f"https://drives.ru{product_link}"
            print(product_link)
            prod_resp = requests.get(product_link)
            if prod_resp.status_code != 200:
                continue
            prod_soup = BeautifulSoup(prod_resp.text, "html.parser")

            code_div = prod_soup.find("div", class_="product__code")
            page_article = None
            if code_div:
                span = code_div.find("span")
                if span:
                    page_article = span.get_text(strip=True)
            if not page_article or page_article != product.article_supplier:
                continue  # если артикул не совпал, пропускаем

            # --- Парсинг изображений ---
            main_images = []
            for a in prod_soup.find_all("a", class_="p-images__slider-item"):
                href = a.get("href")
                if href:
                    if not href.startswith("http"):
                        href = f"https://drives.ru{href}"
                    main_images.append(href)

            dop_images = []
            for img in prod_soup.find_all("img", class_="p-images__dop-img"):
                src = img.get("data-src") or img.get("src")
                if src:
                    if not src.startswith("http"):
                        src = f"https://drives.ru{src}"
                    dop_images.append(src)
            # --- Конец парсинга изображений ---

            # --- Преобразование маленьких доп. изображений в большие ---
            big_dop_images = []
            for img_url in dop_images:
                big_url = re.sub(r"\.[0-9]+x[0-9]+\.png$", ".970.png", img_url)
                big_dop_images.append(big_url)
            # --- Конец преобразования ---

            # --- Новый парсинг названия, описания и характеристик ---
            # Название
            name_tag = prod_soup.find("h1", class_="product__h1")
            name = name_tag.get_text(strip=True) if name_tag else None

            # Описание
            desc = None
            desc_block = prod_soup.find("div", id="description")
            if desc_block:
                desc_inner = desc_block.find("div", class_="desc desc_max ")
                if desc_inner:
                    desc = desc_inner.get_text(strip=True)
            if desc is None:
                # fallback: ищем по заголовку "Описание"
                title_name = prod_soup.find(
                    "div", class_="in-blocks__title-name", string="Описание"
                )
                if title_name:
                    parent_item = title_name.find_parent(
                        "div", class_="in-blocks__item"
                    )
                    if parent_item:
                        desc_inner = parent_item.find("div", class_="desc desc_max")
                        if desc_inner:
                            desc = desc_inner.get_text(strip=True)
            if desc is None:
                # ищем все desc desc_max h-hidden-show, над которыми есть in-blocks__title с Описание
                for desc_inner in prod_soup.find_all("div", class_="desc desc_max"):
                    found = False
                    for sib in desc_inner.previous_siblings:
                        # Пропускаем не-теги
                        if not getattr(sib, "name", None):
                            continue
                        sib_classes = set(sib.get("class", []))
                        print(f"SIB: {sib}, classes: {sib_classes}")  # отладка
                        if "in-blocks__title" in sib_classes:
                            title_name = sib.find("div", class_="in-blocks__title-name")
                            if (
                                title_name
                                and title_name.get_text(strip=True) == "Описание"
                            ):
                                desc = desc_inner.get_text(strip=True)
                                found = True
                                break
                    if found:
                        break

            # Характеристики
            features = {}
            features_block = prod_soup.find(
                "div", class_=lambda x: x and x.startswith("features")
            )
            if features_block:
                for block in features_block.find_all(
                    "div", class_="features-two-val__block"
                ):
                    name_div = block.find("div", class_="features-two-val__name")
                    value_div = block.find("div", class_="features-two-val__value")
                    if name_div and value_div:
                        fname = name_div.get_text(strip=True)
                        fval = value_div.get_text(strip=True)
                        if fname in ("Описание", "Типовой код","Бренд"):
                            continue
                        if fname == "ВхШхГ, мм":
                            nums = re.findall(r"[\d,\.]+", fval)
                            if len(nums) == 3:
                                features["Высота (мм)"] = nums[0]
                                features["Ширина (мм)"] = nums[1]
                                features["Глубина (мм)"] = nums[2]
                            else:
                                features[fname] = fval
                        else:
                            features[fname] = fval
            # --- Конец нового парсинга ---

            # --- Документы с категории ---
            documents = []
            # Найти ссылку на категорию
            cat_block = prod_soup.find("div", class_="product__category")
            cat_a = (
                cat_block.find("a", class_="product__category-item")
                if cat_block
                else None
            )
            if cat_a and cat_a.has_attr("href"):
                cat_url = cat_a["href"]
                print("cat_url", cat_url)
                if not cat_url.startswith("http"):
                    cat_url = f"https://drives.ru{cat_url}"
                try:
                    print("cat_url", cat_url)
                    cat_resp = requests.get(cat_url)
                    if cat_resp.status_code == 200:
                        cat_soup = BeautifulSoup(cat_resp.text, "html.parser")
                        res_block = cat_soup.find("div", class_="series__resources")
                        if res_block:
                            for item in res_block.find_all(
                                "div", class_="series__resources-item"
                            ):
                                h3 = item.find("h3")
                                doc_type = None
                                if h3:
                                    h3_text = h3.get_text(strip=True)
                                    if h3_text == "Инструкции и руководства":
                                        doc_type = {
                                            "type": "Doc",
                                            "type_name": "Руководства и Спецификации",
                                        }
                                    elif h3_text == "Каталоги и брошюры":
                                        doc_type = {
                                            "type": "Other",
                                            "type_name": "Другое",
                                        }
                                    elif h3_text == "Чертежи":
                                        doc_type = {
                                            "type": "DimensionDrawing",
                                            "type_name": "Габаритные чертежи",
                                        }
                                ul = item.find("ul")
                                if doc_type and ul:
                                    for li in ul.find_all("li"):
                                        a = li.find("a")
                                        print("a", a)
                                        if a and a.has_attr("href"):
                                            doc_url = a["href"]
                                            if not doc_url.startswith("http"):
                                                doc_url = f"https://drives.ru{doc_url}"
                                            doc_name = a.get_text(strip=True)

                                            documents.append(
                                                {
                                                    "name": doc_name,
                                                    "url": doc_url,
                                                    "type": doc_type["type"],
                                                    "type_name": doc_type["type_name"],
                                                }
                                            )
                except Exception as e:
                    print(f"Ошибка при парсинге документов: {e}")

            # --- Парсинг хлебных крошек (категория и группа) ---
            category_name = None
            group_name = None
            nav = prod_soup.find("nav", class_="bread__wrap")
            if nav:
                crumb_items = nav.find_all(attrs={"itemprop": "itemListElement"})
                if len(crumb_items) >= 2:
                    meta_cat = crumb_items[1].find("meta", attrs={"itemprop": "name"})
                    if meta_cat:
                        category_name = meta_cat.get("content")
                if len(crumb_items) >= 3:
                    meta_group = crumb_items[2].find("meta", attrs={"itemprop": "name"})
                    if meta_group:
                        group_name = meta_group.get("content")

            results.append(
                {
                    "product_id": product.id,
                    "type_code": type_code,
                    "product_link": product_link,
                    "main_images": main_images,
                    # 'dop_images': dop_images,
                    # 'big_dop_images': big_dop_images,
                    "description": desc,
                    "features": features,
                    "page_article": page_article,
                    "name": name,
                    "documents": documents,
                    "category_name": category_name,
                    "group_name": group_name,
                }
            )
            # [
            #     {
            #         "product_id": 269,
            #         "type_code": "PBC02003",
            #         "product_link": "https://drives.ru/vhodnye-drosseli-peremennogo-toka-dlya-preobrazovatelej-chastoty-veda-vfd-pbc02003/",
            #         "main_images": [
            #             "https://drives.ru/wa-data/public/shop/products/94/32/3294/images/3294/3294.970.png",
            #             "https://drives.ru/wa-data/public/shop/products/94/32/3294/images/3289/3289.970.png",
            #             "https://drives.ru/wa-data/public/shop/products/94/32/3294/images/3290/3290.970.png",
            #             "https://drives.ru/wa-data/public/shop/products/94/32/3294/images/3291/3291.970.png",
            #             "https://drives.ru/wa-data/public/shop/products/94/32/3294/images/3292/3292.970.png",
            #             "https://drives.ru/wa-data/public/shop/products/94/32/3294/images/3293/3293.970.png",
            #         ],
            #         "description": "Входной дроссель – силовая опция, устанавливаемая на входе преобразователя частоты, позволяет подавлять гармонические искажения, генерируемые как самим преобразователем частоты, так и воздействием сети питания.\n\nПреимущества сетевых дросселей\n\n- Защита от гармонических искажений из сети питания, увеличение срока службы и надежности работы преобразователя частоты.\n\n- Защита ПЧ при коротких замыканиях.\n\n- Защита от скачков напряжения при подключении нескольких мощных устройств к одной шине питания.",
            #         "features": {
            #             "Высота (мм)": "145",
            #             "Ширина (мм)": "75",
            #             "Глубина (мм)": "120",
            #             "Масса, кг": "3,2",
            #             "Бренд": "VEDA",
            #             "Крепление, axb": "65x50   4-φ6x12",
            #             "Теплопотери, Вт": "88",
            #             "Мощность ПЧ, кВт": "2,2",
            #             "Номинальный выходной ток, А": "9",
            #         },
            #         "page_article": "PBC02003",
            #         "name": "Входные дроссели переменного тока для преобразователей частоты VEDA VFD — PBC02003 — ACI-C-0009-T4",
            #         "documents": [
            #             {
            #                 "name": "Чертежи входных дросселей переменного тока",
            #                 "url": "https://drives.ru/files/file/197be00061cd599a2823d227c73b2c2eba9",
            #                 "type": "DimensionDrawing",
            #                 "type_name": "Габаритные чертежи",
            #             },
            #             {
            #                 "name": "Чертежи входных дросселей переменного тока Т6",
            #                 "url": "https://drives.ru/files/file/197be00061cd599a2833d227c73b2c2eba9",
            #                 "type": "DimensionDrawing",
            #                 "type_name": "Габаритные чертежи",
            #             },
            #         ],
            #         "category_name": "Низковольтные ПЧ и УПП",
            #         "group_name": "Силовые опции для преобразователей частоты VEDA VFD",
            #     }
            # ]
            print(results)
            for result in results:
                groupe, categ =  get_category_delta(supplier, vendor,result['category_name'], result['group_name'])
                print(groupe, categ)
               
                if product.group_supplier == None or product.group_supplier == "":
                    product.group_supplier = groupe
                if product.group_supplier == None or product.group_supplier == "":
                    product.group_supplier = groupe

                if product.category_supplier == None or product.category_supplier == "":
                    product.category_supplier = categ
                if product.category_supplier == None or product.category_supplier == "":
                    product.category_supplier = categ
                
                if product.description == None or product.description == "":
                    product.description = result['description']
                    
                product.name = result['name']
                if product.name == None or product.name == "":
                    product.name = result['name']
                product.autosave_tag = True
                product._change_reason = "Автоматическое"    
                product.save()
                
            
            
            
            
            
            
            
            found = True
            break  # нашли нужный товар, дальше не ищем
        if not found:
            print(f"Товар с артикулом {type_code} не найден на drives.ru")

    return results


def parse_drives_ru_category():
    """
    Парсит категории и группы VEDA с drives.ru.
    Категории и группы ищутся внутри блока .cat-prod-grid, если на странице есть <h3 class="main__title-2">Приводная техника и средства автоматизации VEDA</h3>.
    Категория: .cat-prod-name, группы: .cat-prod-sub-name (в том числе внутри .hidden-list)
    Возвращает список словарей: [{category_name, category_url, groups: [{group_name, group_url}]}]
    """
    import requests
    from bs4 import BeautifulSoup

    supplier = Supplier.objects.get(slug="veda-mc")
    vendor = Vendor.objects.get(slug="veda")

    url = "https://drives.ru/products/"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Ошибка запроса: {response.status_code}")
        return []
    soup = BeautifulSoup(response.text, "html.parser")

    # Проверяем наличие нужного заголовка
    h3 = soup.find("h3", class_="main__title-2")
    if not h3:
        print("Заголовок не найден или не совпадает")
        return []

    cat_grid = soup.find("div", class_="cat-prod-grid")
    if not cat_grid:
        print("cat-prod-grid не найден")
        return []

    categories = []
    for cat_prod in cat_grid.find_all("div", class_="cat-prod", recursive=False):
        # Категория
        cat_name_div = cat_prod.find("div", class_="cat-prod-name")
        if not cat_name_div:
            continue
        cat_a = cat_name_div.find("a")
        if not cat_a:
            continue
        category_name = re.sub(r"\s+", " ", cat_a.get_text(strip=True))
        category_url = cat_a["href"]
        if not category_url.startswith("http"):
            category_url = f"https://drives.ru{category_url}"

        # Группы (основные)
        groups = []
        for group_div in cat_prod.find_all(
            "div", class_="cat-prod-sub-name", recursive=False
        ):
            group_a = group_div.find("a")
            if group_a:
                group_name = re.sub(r"\s+", " ", group_a.get_text(strip=True))

                groups.append({"group_name": group_name})
        # Группы (скрытые)
        hidden_list = cat_prod.find("div", class_="hidden-list")
        if hidden_list:
            for group_div in hidden_list.find_all("div", class_="cat-prod-sub-name"):
                group_a = group_div.find("a")
                if group_a:
                    group_name = re.sub(r"\s+", " ", group_a.get_text(strip=True))

                    groups.append(
                        {
                            "group_name": group_name,
                        }
                    )
        categories.append({"category_name": category_name, "groups": groups})

    for category in categories:
        print(category["category_name"])
        try:
            categ = SupplierCategoryProduct.objects.get(
                supplier=supplier,
                vendor=vendor,
                name=category["category_name"],
            )

        except SupplierCategoryProduct.DoesNotExist:
            categ = SupplierCategoryProduct(
                supplier=supplier,
                vendor=vendor,
                name=category["category_name"],
            )
            categ.save()

        for group_item in category["groups"]:
            try:
                grope = SupplierGroupProduct.objects.get(
                    supplier=supplier,
                    vendor=vendor,
                    category_supplier=categ,
                    name=group_item["group_name"],
                )

                grope.save()

            except SupplierGroupProduct.DoesNotExist:
                grope = SupplierGroupProduct(
                    supplier=supplier,
                    vendor=vendor,
                    category_supplier=categ,
                    name=group_item["group_name"],
                )
                grope.save()

    return categories

# категории поставщика промповер для товара
def get_category_delta(supplier, vendor, category,group):
    from apps.supplier.models import (
        SupplierCategoryProduct,
        SupplierCategoryProductAll,
        SupplierGroupProduct,
    )
    groupe = None
    categ = None
    
    if group:
        groupe = SupplierGroupProduct.objects.get(
                supplier=supplier, vendor=vendor, name=group
            )
        categ = groupe.category_supplier
    elif category:
        groupe = None
        categ = SupplierCategoryProduct.objects.get(
                    supplier=supplier, vendor=vendor, name=category
                )
        
    
    ("return get_category_delta", groupe, categ)

    return (groupe, categ)