import datetime
from fileinput import filename
import os
import re
import threading
import zipfile
import csv
from simple_history.utils import update_change_reason


from apps.core.models import Currency, Vat


from apps.logs.utils import error_alert


from apps.product.models import Lot
from apps.supplier.models import SupplierGroupProduct
from project.settings import MEDIA_ROOT



items_categ = [
    {"ustrojstva-plavnogo-puska-od": "Устройства плавного пуска"},  # OPTIMUS DRIVE
    {"enkoderyi-od": "Энкодеры"},  # OPTIMUS DRIVE
    {
        "kommutatoryi-razvetviteli-od": "Промышленные коммутаторы и разветвители"
    },  # OPTIMUS DRIVE
    {"paneli-operatora-od": "Панели оператора"},  # OPTIMUS DRIVE
    {"preobrazovateli-chastotyi-od": "Преобразователи частоты"},  # OPTIMUS DRIVE \ SINE
    {"promyishlennyie-kontrolleryi-od": "Программируемые контроллеры"},  # OPTIMUS DRIVE
    {"temperaturnyie-kontrolleryi-od": "Температурные контроллеры"},  # OPTIMUS DRIVE
    # {"servodvigateli": "Сервоприводы и редукторы"},
    # {"texnicheskoe-zrenie": "Техническое зрение"},  # общая группа{
    {"servodvigateli-od": "Сервоприводы и редукторы"},  # VEICHI
    {"servodvigateli-sch-od": "Серводвигатели серии SCH SAVCH (архив)"},  # SAVCH архив
    {"servousiliteli-od": "Сервоусилители"},  # VEICHI SAVCHархив
    {"texnicheskoe-zrenie-2-od": "Техническое зрение: Считыватели кодов"},  # HIKROBOT
    {"texnicheskoe-zrenie-3d-od": "Техническое зрение : 3D Камеры"},  # HIKROBOT
    {
        "texnicheskoe-zrenie-4-kontrolleryi-od": "Техническое зрение: Контроллеры машинного зрения"
    },  # HIKROBOT
    {
        "texnicheskoe-zrenie-5-obektivyi-od": "Техническое зрение : Объективы"
    },  # HIKROBOT
    {
        "texnicheskoe-zrenie-6-teleczentricheskie-obektivyi-od": "Техническое зрение : Телецентрические объективы"
    },  # HIKROBOT
]

def add_file_optimus(new_file, obj):

    try:
        # распаковка архива

        path = os.path.join(MEDIA_ROOT, str(new_file))
        new_dir = "{0}/{1}/{2}/{3}".format(
            MEDIA_ROOT, "price", "optimus-drive", "files"
        )
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        extension = str(new_file).split(".")[-1]

        if extension == "zip":
            with zipfile.ZipFile(path, "r") as zip_ref:
                item = zip_ref.extractall(path=new_dir)
                return new_dir

        else:

            error = "file_error"
            location = "Загрузка фаилов optimus"
            info = f"фаил такого формата нельзя считать"
            e = error_alert(error, location, info)
    except Exception as e:
        print(e)
        error = "file_error"
        location = "Загрузка фаилов optimus"

        info = f"ошибка при чтении фаила"
        e = error_alert(error, location, info)


def add_optimus_product():
    from apps.supplier.models import SupplierCategoryProduct, SupplierGroupProduct
    from apps.supplier.models import Supplier

    obj = Supplier.objects.get(slug="optimus-drive")

    new_dir = "{0}/{1}/{2}/{3}".format(MEDIA_ROOT, "price", "optimus-drive", "files")
    # первое сохранение категорий
    category_supplier = SupplierCategoryProduct.objects.filter(supplier=obj).exists()
    if category_supplier == False:
        for item_name_categ in items_categ:
            name = list(item_name_categ.values())[0]
            slug = list(item_name_categ.keys())[0]
            try:
                categ = SupplierCategoryProduct.objects.get(
                    name=name, slug=slug, supplier=obj
                )
                
            except SupplierCategoryProduct.DoesNotExist:
                categ = SupplierCategoryProduct(
                    name=name, slug=slug, supplier=obj, autosave_tag=True
                )
                categ.save()


    # перебор фаилов и считывание
    file_names = []

    for entry in os.scandir(new_dir):
        if entry.is_file():
            file_names.append(entry.name)
    i = 0
    for file_name in file_names:
        file_name_no_attr = file_name.split(".")
  
        category_supplier = SupplierCategoryProduct.objects.filter(
                    supplier=obj, slug=file_name_no_attr[0]
                ).exists()
        
        if category_supplier == True:
            i += 1
            if i > 0:
                try:
                    optimus_written_file(file_name, obj, new_dir)

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

            info = f"Новый фаил {file_name}"
            e = error_alert(error, location, info)

def optimus_written_file(file_name, obj, new_dir):
    from apps.core.utils import (
        create_article_motrum,
        get_file_path_add,
        save_file_product,
    )
    from bs4 import BeautifulSoup
    from apps.supplier.models import (
        SupplierGroupProduct,
        SupplierCategoryProduct,
        Vendor,
    )
    from apps.product.models import Price, Product, Stock, ProductImage, ProductProperty



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
        it = 0
        for row2 in reader2:
            it += 1
            try:
                article_supplier = row2["Модель"]

                categ = file_name.split(".")

                category_supplier = SupplierCategoryProduct.objects.get(
                    supplier=obj, slug=categ[0]
                )

                print(category_supplier)
                group_supplier = SupplierGroupProduct.objects.get_or_create(
                    supplier=obj,
                    name=row2["Серия"],
                    category_supplier=category_supplier,
                )
                tds = []
                if "Полное описание" in row2:
                    description_item = row2["Полное описание"]

                    if description_item != "":
                        description_arr = description_item.split(
                            '<table class="table-cart">'
                        )

                        if len(description_arr) > 1:
                            description_arr_replace = description_arr[0].replace(
                                "</li>", ". "
                            )
                            res_description_arr_replace = re.sub(
                                r"<[^>]+>", "", description_arr_replace, flags=re.S
                            )
                            description = res_description_arr_replace

                            # description_arr_split = description_arr[1].split('<div class="container">')

                            # description_arr2 = description_arr_split[0]
                            # print(description_arr2)

                            soup = BeautifulSoup(description_item, "html.parser")
                            quotes = soup.find_all("table", class_="table-cart")

                            for div in quotes:
                                rows = div.findAll("tr")
                                for row in rows:
                                    r = row.findAll("td")
                                    tds.append(row.findAll("td"))

                        else:
                            res_description_replace = re.sub(
                                r"<[^>]+>", "", row2["Полное описание"], flags=re.S
                            )
                            description = res_description_replace

                    else:
                        res_description_replace = re.sub(
                            r"<[^>]+>", "", row2["Краткое описание"], flags=re.S
                        )
                        description = res_description_replace
                       
            # если колонка содержимое пустая берем описание
                else:
                    if "Описание" in row2:
                        description_arr_replace = row2["Описание"].replace(
                            "</li>", ". "
                        )
                        res_description_arr_replace = re.sub(
                            r"<[^>]+>", "", description_arr_replace, flags=re.S
                        )
                        description = res_description_arr_replace
                    else:
                        description = None
                        
                name = row2["Краткое описание"]
                if name == "":
                    name = description
               
                # прайс  
                price = row2["Цена"].replace(" ", "")
                if price == "" or price == "n":
                    extra = True
                    price_supplier = 0

                else:
                    extra = False
                    price_supplier_float = float(price)
                    price_supplier = price_supplier_float
                    # percent_convert = price_supplier_float / 100 * 1
                    # price_supplier = price_supplier_float + percent_convert

                vat_catalog = Vat.objects.get(name=20)
                currency = Currency.objects.get(words_code="USD")
# сохранение изображений
                def save_image(
                    article,
                ):
                    image_link = ""
                    if "Изображение" in row2:
                        img_big = row2["Изображение"].replace(" ", "")
                        img_small = row2["Изображение при увеличении"].replace(" ", "")
 
                        if img_big != "" and img_big != "https://optimusdrive.ru/" and img_big != "https://optimusdrive.ru/imagesod/catalog/nfod3.jpg":
                            image_link = img_big
                        elif (
                            img_small != "" and img_small != "https://optimusdrive.ru/" and img_big != "https://optimusdrive.ru/imagesod/catalog/nfod3.jpg"
                        ):
                            image_link = img_small
                        print(image_link)

                        if image_link != "":

                            image = ProductImage.objects.create(product=article)
                            update_change_reason(image, "Автоматическое")
                            image_path = get_file_path_add(image, image_link)
                          
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
                    try:
                        stock_prod = Stock.objects.get(prod=article)
                        
                    except Stock.DoesNotExist:
                        stock_supplier = None
                        lot = Lot.objects.get(name="штука")
                        
                        stock_prod = Stock(
                            prod=article, 
                            lot=lot, 
                            stock_supplier = stock_supplier,
                            data_update = datetime.datetime.now()
                        )
                        stock_prod._change_reason = 'Автоматическое'
                        stock_prod.save() 
                    
                # свойства из из общей колонки    
                props_product = ProductProperty.objects.filter(product=article).exists()
                if props_product == False:

                    if tds != []:
                        i = 0
                        for td in tds:
                            i += 1
                            if i > 1:
                                if td != []:
                                    print(td)
                                    value_props_no_br = str(td[1]).replace("<br>", ". ")
                                    value_props_no_br = str(td[1]).replace("<br/>", ". ")
                                    name_props = re.sub(
                                        r"<[^>]+>", "", str(td[0]), flags=re.S
                                    )
                                    value_props = re.sub(
                                        r"<[^>]+>", "", value_props_no_br, flags=re.S
                                    )
                                    props_product = ProductProperty(product=article)
                                    props_product.name = name_props

                                    props_product.value = value_props
                                    props_product.save()
                                    update_change_reason(
                                        props_product, "Автоматическое"
                                    )
                # свойства из отдельных колонок
                save_optimus_props(row2, article)

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
                    price_product._change_reason = "Автоматическое"
                    price_product.save()
                    
                    
            except Exception as e:
                print(e)
                error = "file_error"
                location = "Загрузка фаилов Delta"

                info = f"ошибка при чтении строки артикул {row2["Модель"]}"
                e = error_alert(error, location, info)
            finally:
                continue
# свойсва если есть колонки со свойствами            
def save_optimus_props(row2, article):
    from apps.product.models import ProductProperty
# колонки кроме основных
    row_list = list(row2)
    remove_list = {
        "Модель",
        "Серия",
        "Краткое описание",
        "Описание",
        "Полное описание",
        "Позиция в меню",
        "Цена",
        "Изображение",
        "Изображение при увеличении",
    }

    props_product = ProductProperty.objects.filter(product=article).exists()
    if props_product == False:

        for remove_item in remove_list:
            if remove_item in row_list:
                row_list.remove(remove_item)
       
        for row_row_list in row_list:
            name_props = row_row_list
            value_props = row2[row_row_list]
       
            if row_row_list != None and name_props != "":
                if "<br>" in name_props:
                    name_props = name_props.replace("<br>", " ,")
                    
                if "<br>" in value_props:
                    value_props = value_props.replace("<br>", " ,")

                if "</sup>" in name_props:
                    name_props = name_props.replace("</sup>", "*")
                    name_props = name_props.replace("<sup>", "")
                if '<span class="icon mdi mdi-check"></span>' in value_props:
                    value_props = "Да"

                if value_props != "" and value_props != " ":
                    props_product = ProductProperty(product=article)
                    props_product.name = name_props
                    props_product.value = value_props
                    props_product.save()
                    update_change_reason(props_product, "Автоматическое")
