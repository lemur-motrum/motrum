import datetime
import os
import traceback
from apps.core.models import Currency, Vat
from apps.core.utils import (
    create_article_motrum,
    get_file_path_add,
    save_file_product,
    save_update_product_attr,
)
from apps.logs.utils import error_alert
from apps.product.models import Lot, Price, Product, Stock
from apps.supplier.models import (
    Supplier,
    SupplierCategoryProduct,
    SupplierGroupProduct,
    Vendor,
)
import requests
from project.settings import MEDIA_ROOT
from simple_history.utils import update_change_reason
import re
from django.utils.text import slugify
from pytils import translit
from urllib.parse import urljoin


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
    from apps.product.models import (
        Product,
        ProductImage,
        ProductDocument,
        ProductProperty,
    )
    from apps.supplier.models import Vendor
    import requests
    from bs4 import BeautifulSoup

    supplier = Supplier.objects.get(slug="veda-mc")
    vendor = Vendor.objects.get(slug="veda")
    # products = Product.objects.filter(article_supplier__in=['MCD13003', 'MCD12208', 'PBV00010'])
    products = Product.objects.filter(supplier=supplier, vendor=vendor)
    results = []
    
    for product in products:
        try:
            result_one = []
            print(product)
            type_code = product.article_supplier  # используем артикул напрямую
            if not type_code:
                continue

            search_url = f"https://drives.ru/search/?query={type_code}"
        
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
                            if fname in ("Описание", "Типовой код", "Бренд"):
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
            
                    if not cat_url.startswith("http"):
                        cat_url = f"https://drives.ru{cat_url}"
                    try:
            
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
                                    
                                            if a and a.has_attr("href"):
                                                doc_url = a["href"]
                                                doc_url = urljoin("https://drives.ru", doc_url)
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
                result_one = [{
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
                    }]
                print(results)

            
                for result in result_one:

                    def save_document(doc, product):

                        base_dir = "products"
                        path_name = "documents"
                        base_dir_supplier = supplier
                        base_dir_vendor = vendor

                        new_dir = "{0}/{1}/{2}/{3}/{4}".format(
                            MEDIA_ROOT,
                            base_dir,
                            base_dir_supplier,
                            base_dir_vendor,
                            path_name,
                        )
                        dir_no_path = "{0}/{1}/{2}/{3}".format(
                            base_dir,
                            base_dir_supplier,
                            base_dir_vendor,
                            path_name,
                        )
                        if not os.path.exists(new_dir):
                            os.makedirs(new_dir)

                        if doc:
                            for doc_item in doc:
                                url = doc_item["url"]
                                # Проверка наличия расширения файла
                                doc_filename = url.split("/")[-1]
                                _, ext = os.path.splitext(doc_filename)
                                if not ext:
                                    continue  # если нет расширения, пропускаем
                                
                                other_doc = ProductDocument.objects.filter(
                                    link=url,
                                )
                                print(other_doc)
                                if other_doc:
                                    other_doc_first = other_doc.first()
                                    doc = ProductDocument.objects.create(
                                        product=product,
                                        document=other_doc_first.document,
                                        link=other_doc_first.link,
                                        name=doc_item["name"],
                                        type_doc=doc_item["type"].capitalize(),
                                    )
                                else:
                                    slugish = translit.translify(doc_item["name"])
                                    base_slug = slugify(slugish)
                                    doc_name = base_slug
                                    doc = ProductDocument.objects.create(product=product)
                                    update_change_reason(doc, "Автоматическое")
                                    doc_list_name = url.split("/")
                                    doc_name = doc_list_name[-1]
                                    images_last_list = url.split(".")
                                    type_file = "." + images_last_list[-1]
                                    link_file = f"{new_dir}/{doc_name}"
                                    r = requests.get(url, stream=True)
                                    with open(os.path.join(link_file), "wb") as ofile:
                                        ofile.write(r.content)
                                    doc.document = f"{dir_no_path}/{doc_name}"
                                    doc.link = url
                                    doc.name = doc_item["name"]
                                    doc.type_doc = doc_item["type"].capitalize()
                                    doc.save()
                                    update_change_reason(doc, "Автоматическое")

                    def save_image(
                        product,
                    ):
                        if len(result["main_images"]) > 0:
                            for img_item in result["main_images"]:
                                img = img_item
                                image = ProductImage.objects.create(product=product)
                                update_change_reason(image, "Автоматическое")
                                image_path = get_file_path_add(image, img)
                                p = save_file_product(img, image_path)
                                image.photo = image_path
                                image.link = img
                                image.save()
                                update_change_reason(image, "Автоматическое")

                    groupe, categ = get_category_delta(
                        supplier, vendor, result["category_name"], result["group_name"]
                    )
                

                    if product.group_supplier == None or product.group_supplier == "":
                        product.group_supplier = groupe
                    if product.group_supplier == None or product.group_supplier == "":
                        product.group_supplier = groupe

                    if product.category_supplier == None or product.category_supplier == "":
                        product.category_supplier = categ
                    if product.category_supplier == None or product.category_supplier == "":
                        product.category_supplier = categ

                    if product.description == None or product.description == "":
                        product.description = result["description"]

                    product.name = result["name"]
                    if product.name == None or product.name == "":
                        product.name = result["name"]
                    product.autosave_tag = True
                    product._change_reason = "Автоматическое"
                    product.save()

                    image = ProductImage.objects.filter(product=product).exists()
                    if image == False:
                        save_image(product)
                
                    doc = ProductDocument.objects.filter(
                            product=product
                        ).exists()
                    if doc == False:
                        save_document(result["documents"], product)
                        
                    props = ProductProperty.objects.filter(
                                        product=product
                                    ).exists()
                                    
                    if props == False:
                        for name, value in features.items():
                            property_product = ProductProperty(
                                product=product,
                                name=name,
                                value=value,
                            )
                            property_product.save()
                            update_change_reason(property_product, "Автоматическое")

                found = True
                break  # нашли нужный товар, дальше не ищем
            if not found:
                print(f"Товар с артикулом {type_code} не найден на drives.ru")
        except Exception as e:
            print(e)
            tr = traceback.format_exc()
            error = "file_api_error"
            location = "Загрузка крыса Veda MC"
            info = f"ошибка при чтении товара артикул: {product}. Тип ошибки:{e}{tr}"
            e = error_alert(error, location, info)
        finally:
            continue
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
def get_category_delta(supplier, vendor, category, group):
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
