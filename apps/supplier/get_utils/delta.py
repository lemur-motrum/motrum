from fileinput import filename
import os
import re
import zipfile
import csv
from simple_history.utils import update_change_reason


from apps.core.models import Currency, Vat


from apps.logs.utils import error_alert
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
    {"vyigruzka-shkafyi-upravleniya-d": "Шкафы управления"},
    {"vyigruzka-temperaturnyie-kontrolleryi-d": " Температурные контроллеры"},
    {
        "vyigruzka-tormoznyie-moduli-i-rezistoryi-d": "Тормозные резисторы и тормозные модули"
    },
    {"vyigruzka-tz-d": "Техзрение"},
    {"vyigruzka-upp-d": "Устройства плавного пуска"},
]


def add_file_delta(new_file, obj):

    from apps.supplier.models import SupplierCategoryProduct
    try:
        # распаковка архива
        path = os.path.join(MEDIA_ROOT, str(new_file))
        new_dir = "{0}/{1}/{2}/{3}".format(MEDIA_ROOT, "price", "delta", "files")
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        extension = str(new_file).split('.')[-1]    
        if extension == ".zip":
            with zipfile.ZipFile(path, "r") as zip_ref:
                item = zip_ref.extractall(path=new_dir)
                print(item)

            # первое сохранение категорий
            category_supplier = SupplierCategoryProduct.objects.filter(supplier=obj).exists()

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
        
            for file_name in file_names:
                try:
                    delta_written_file(file_name, obj, new_dir)
                except Exception as e: 
                    print(e)
                    error = "file_error"
                    location = "Загрузка фаилов Delta"
          
                    info = f"ошибка при чтении фаила{file_name}"
                    e = error_alert(error, location, info)
                finally:    
                    continue 
        else:
            error = "file_error"
            location = "Загрузка фаилов Delta"
            info = f"фаил такого формата нельзя считать"
            e = error_alert(error, location, info)
    except Exception as e: 
            print(e)
            error = "file_error"
            location = "Загрузка фаилов Delta"
          
            info = f"ошибка при чтении фаила"
            e = error_alert(error, location, info)
             

def delta_written_file(file_name, obj, new_dir):
    from apps.core.utils import (
        create_article_motrum,
        get_file_path_add,
        save_file_product,
    )
    from bs4 import BeautifulSoup
    from apps.supplier.models import SupplierGroupProduct, SupplierCategoryProduct
    from apps.product.models import Price, Product, Stock, ProductImage ,ProductProperty

    path = f"{new_dir}/{file_name}"
    # получение названий столюцов
    fieldnames = []
    with open(path, "r", newline="", encoding="windows-1251") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for r in row:
                if type(r) == str:
                    fieldnames = r.split(";")
    # считывание столбцов по названиям 
    with open(
        path,
        "r",
        newline="",
        encoding="windows-1251",
    ) as csvfile2:
        reader2 = csv.DictReader(csvfile2, delimiter=";")
        for row2 in reader2:
            article_supplier = row2["Модель"]

            categ = file_name.split(".")
            category_supplier = SupplierCategoryProduct.objects.get(
                supplier=obj, slug=categ[0]
            )
            group_supplier = SupplierGroupProduct.objects.get_or_create(
                supplier=obj,
                name=row2["Серия"],
                category_supplier=category_supplier,
            )

            
            description_item = row2["Содержимое(контент)"]
          
            if description_item != "":
                description_arr = description_item.split('<div class="container">')
                if len(description_arr) > 1:
                    description_arr_replace = description_arr[0].replace("</li>", ". ")
                    res_description_arr_replace = re.sub(
                        r"<[^>]+>", "", description_arr_replace, flags=re.S
                    )
                    description = res_description_arr_replace
                    description_arr2 = description_arr[1].split("</tr>")
                else:
                    res_description_replace = re.sub(
                    r"<[^>]+>", "", row2["Краткое описание"], flags=re.S
                )
                    description = res_description_replace    

            else:
                res_description_replace = re.sub(
                    r"<[^>]+>", "", row2["Краткое описание"], flags=re.S
                )
                description = res_description_replace
                # tds = []
                # soup = BeautifulSoup(description_arr[1])
                # quotes = soup.find_all('table', class_='table-custom-primary')
                # for div in quotes:
                #     rows = div.findAll('tr')
                #     for row in rows :
                #         r = row.findAll('td')
                #         tds.append(row.findAll('td'))
           
            
            name = row2["Расширенный заголовок"]
            if name == "":
                name = description
            # прайс
            if row2["Позиция в меню"] == "":
                price = row2["Банер на странице"]
            else:
                price = row2["Цена"]
                
            if price == "" or price == "n":
                extra = True
                price_supplier = 0

            else:
                extra = False
                price_supplier_float = float(price)
                percent_convert = price_supplier_float / 100 * 1
                price_supplier = price_supplier_float + percent_convert
              

            vat_catalog = Vat.objects.get(name=20)
            currency = Currency.objects.get(words_code="USD")

            def save_image(
                article,
            ):
                image_link = ''
                img_big = row2["Изображение"]
                img_small = row2["Изображение при увеличении"]
                print(img_big,img_small)
                if img_big != "" and img_big != "https://deltronics.ru/":
                    image_link = img_big
                    print(1111111111111111)
                elif img_small != "" and img_small != "https://deltronics.ru/":
                    image_link = img_small
                    print(222222222222)
                
                
                if image_link != "":
                    
                    image = ProductImage.objects.create(product=article)
                    update_change_reason(image, "Автоматическое")
                    image_path = get_file_path_add(image, image_link)
                    print(image_link)
                    print(image_path)
                    p = save_file_product(image_link, image_path)
                    image.photo = image_path
                    image.link = image_link
                    image.save()
                    update_change_reason(image, "Автоматическое")
           
            # основной товар
            try:
                article = Product.objects.get(
                    supplier=obj, article_supplier=article_supplier
                )
                image = ProductImage.objects.filter(product=article).exists
                if image == False:
                    save_image(article)

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
                article.save()
                
                update_change_reason(article, "Автоматическое")
                save_image(article)
            save_delta_props(row2,article)
            print(article)
            # цены товара
            try:
                price_product = Price.objects.get(prod=article)

            except Price.DoesNotExist:
                price_product = Price(prod=article)

            finally:
                price_product.currency = currency
                price_product.price_supplier = price_supplier
                price_product.vat = vat_catalog
                price_product.vat_include = True
                price_product.extra_price = extra
                price_product.save()
                update_change_reason(price_product, "Автоматическое")

def save_delta_props(row2,article):
    from apps.product.models import ProductProperty
    
    row_list = list(row2)
    remove_list = {"Модель",'Серия', 'Расширенный заголовок', 'Описание', 'Краткое описание', 'Аннотация (введение)', 'Содержимое(контент)', 'Позиция в меню', 'Цена', 'Банер на странице', 'Изображение', 'Изображение при увеличении'}
    for remove_item in remove_list:
        row_list.remove(remove_item)
 
    for row_row_list in row_list:
        name_props = row_row_list
        if row_row_list != None:
            if "<br>" in name_props:
                name_props = name_props.replace("<br>", " ,") 
                
            value_props = row2[row_row_list]
            if value_props != "":
                try:
                    props_product = ProductProperty.objects.get(product=article)

                except ProductProperty.DoesNotExist:
                    props_product = ProductProperty(product=article)
                    props_product.name = name_props
                    
                    props_product.value = value_props
                    props_product.save()
                    update_change_reason(props_product, "Автоматическое")

    
           
            
        
            
        
    
