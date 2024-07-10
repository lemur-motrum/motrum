from fileinput import filename
import os
import re
import zipfile
import csv
from simple_history.utils import update_change_reason


from apps.core.models import Currency, Vat



from project.settings import MEDIA_ROOT

items_name = [
    {"vyigruzka-chpu-d": "ЧПУ"},
    {"vyigruzka-datchiki-d": " датчики"},
    {"vyigruzka-drosseli-d": "тормозные дроссели"},
    {"vyigruzka-enkoderyi-d": "энкодеры"},
    {"vyigruzka-istochniki-pitaniya-d": "источники питания"},
    {"vyigruzka-kip-d": "Приборы КИПиА"},
    {"vyigruzka-kommunikaczionnyie-moduli-d": "коммуникационные модули"},
    {"vyigruzka-kommutatoryi-ethernet-d": "коммутаторы ethernet"},
    {"vyigruzka-moduli-rekuperaczii-d": "модули рекуперации"},
    {"vyigruzka-pch-d": "Преобразователь частоты"},
    {"vyigruzka-plk-d": "ПЛК"},
    {"vyigruzka-po-d": "Панели оператора"},
    {"vyigruzka-robotyi-d": "Роботы"},
    {"vyigruzka-servo-d": "Сервоприводы"},
    {"vyigruzka-shkafyi-upravleniya-d ": "Шкафы управления"},
    {"vyigruzka-temperaturnyie-kontrolleryi-d": " Температурные контроллеры"},
    {
        "vyigruzka-tormoznyie-moduli-i-rezistoryi-d": "Тормозные резисторы и тормозные модули"
    },
    {"vyigruzka-tz-d": "Техзрение"},
    {"vyigruzka-upp-d": "Устройства плавного пуска"},
]


def add_file_delta(new_file, obj):

    from apps.supplier.models import SupplierCategoryProduct

    # распаковка архива
    path = os.path.join(MEDIA_ROOT, str(new_file))
    new_dir = "{0}/{1}/{2}/{3}".format(MEDIA_ROOT, "price", "delta", "files")
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(path=new_dir)

    # первое сохранение категорий
    category_supplier = SupplierCategoryProduct.objects.filter(supplier=obj).exists()
    print(category_supplier)
    if category_supplier == False:
        for item_name_categ in items_name:
            name = list(item_name_categ.values())[0]
            slug = list(item_name_categ.keys())[0]
            categ = SupplierCategoryProduct(
                name=name, slug=slug, supplier=obj, autosave_tag=True
            )
            categ.save()

    file_names = []

    for entry in os.scandir(new_dir):
        if entry.is_file():
            file_names.append(entry.name)
    i = 0
    print(file_names)
    for file_name in file_names:
        i += 1
        if i < 2:
            delta_written_file(file_name, obj, new_dir)


def delta_written_file(file_name, obj, new_dir):
    from apps.core.utils import create_article_motrum,get_file_path_add, save_file_product
    from bs4 import BeautifulSoup
    from apps.supplier.models import SupplierGroupProduct, SupplierCategoryProduct,ProductImage
    from apps.product.models import Price, Product
  
  

    path = f"{new_dir}/{file_name}"
    fieldnames = []
    with open(path, "r", newline="", encoding="windows-1251") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for r in row:
                if type(r) == str:
                    fieldnames = r.split(";")

    with open(
        path,
        "r",
        newline="",
        encoding="windows-1251",
    ) as csvfile2:
        reader2 = csv.DictReader(csvfile2, delimiter=";")
        for row2 in reader2:
            article_supplier = (row2["Модель"],)

            categ = file_name.split(".")
            category_supplier = SupplierCategoryProduct.objects.get(
                supplier=obj, slug=categ[0]
            )
            group_supplier = SupplierGroupProduct.objects.get_or_create(
                supplier=obj,
                name=row2["Серия"],
                category_supplier=category_supplier,
            )

            name = (row2["Расширенный заголовок"],)
            description_item = row2["Содержимое(контент)"]

            if description_item != "":
                description_arr = description_item.split('<div class="container">')
                description_arr_replace = description_arr[0].replace("</li>", ". ")
                res_description_arr_replace = re.sub(
                    r"<[^>]+>", "", description_arr_replace, flags=re.S
                )
                description = res_description_arr_replace
                description_arr2 = description_arr[1].split("</tr>")

            else:
                description = row2["Краткое описание"]
                # tds = []
                # soup = BeautifulSoup(description_arr[1])
                # quotes = soup.find_all('table', class_='table-custom-primary')
                # for div in quotes:
                #     rows = div.findAll('tr')
                #     for row in rows :
                #         r = row.findAll('td')
                #         tds.append(row.findAll('td'))

            # прайс
            price = row2["Цена"]
            if price == "" or price == "n":
                extra = True
                price_supplier = 0

            else:
                extra = False
                price_supplier_float = float(price)
                percent_convert = price_supplier_float / 100 * 1
                price_supplier = price_supplier_float + percent_convert
                print(price_supplier)

            vat_catalog = Vat.objects.get(name=20)
            currency = Currency.objects.get(words_code="USD")

            def save_image(
                article,
            ):
                
                img_big = row2["Изображение"]
                img_small = row2["Изображение при увеличении"]
                
                if img_big != "":
                    image_link = img_big
                # elif:
                #     image_link = img_big    
                
                image = ProductImage.objects.create(product=article)
                update_change_reason(image, "Автоматическое")
                image_path = get_file_path_add(image, img)
                p = save_file_product(img, image_path)
                image.photo = image_path
                image.link = img
                image.save()
                update_change_reason(image, "Автоматическое")

            # основной товар
            try:
                article = Product.objects.get(
                    supplier=obj, article_supplier=article_supplier
                )

            except Product.DoesNotExist:
                new_article = create_article_motrum(obj.id)
                article = Product(
                    article=new_article,
                    supplier=obj,
                    vendor=None,
                    article_supplier=article_supplier,
                    name=name,
                    description=description,
                    category_supplier_all=None,
                    group_supplier=group_supplier[0],
                    category_supplier=category_supplier,
                )
                # article.save()

                # update_change_reason(article, "Автоматическое")

                # save_all_doc(data_item,article)
            # # цены товара
            # try:
            #     price_product = Price.objects.get(prod=article)

            # except Price.DoesNotExist:
            #     price_product = Price(prod=article)

            # finally:
            #     price_product.currency = currency
            #     price_product.price_supplier = price_supplier
            #     price_product.vat = vat_catalog
            #     price_product.vat_include = True
            #     price_product.extra_price = extra
            #     # price_product.save()
            # update_change_reason(price_product, "Автоматическое")

        print(sfsf)
