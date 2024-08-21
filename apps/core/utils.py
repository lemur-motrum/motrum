# расчет цены
import datetime
import random
import re
import shutil
import requests
import hashlib
import os
import traceback


# from apps import supplier
from apps import supplier
from apps.core.models import CurrencyPercent
from apps.logs.utils import error_alert



from project.settings import MEDIA_ROOT
from simple_history.utils import update_change_reason


# цена мотрум со скидкой
def get_price_motrum(
    item_category, item_group, vendors, rub_price_supplier, all_item_group,supplier
):
    from apps.supplier.models import (
        Discount,
    )
    print(12312312312313)
    print(item_category.name)
    print(item_group.name)
    print(all_item_group.name)
    
    motrum_price = rub_price_supplier
    percent = 0
    sale = [None]

    # получение процента функция
    def get_percent(item):
        for i in item:
            return i.percent

    if all_item_group and percent == 0:
        discount_all_group = Discount.objects.filter(
            category_supplier_all=all_item_group.id,
            is_tag_pre_sale=False,
        )
       

        if discount_all_group:
            percent = get_percent(discount_all_group)
            sale = discount_all_group

        # скидка по группе

    if item_group and percent == 0:

        discount_group = Discount.objects.filter(
            category_supplier_all__isnull=True,
            group_supplier=item_group.id, is_tag_pre_sale=False
        )
        
     
        if discount_group:
            percent = get_percent(discount_group)
            sale = discount_group
         
            # if percent != 0

    # скидка по категории
    if item_category and percent == 0:
      
        discount_categ = Discount.objects.filter(
            category_supplier_all__isnull=True,
            group_supplier__isnull=True,
            category_supplier=item_category.id,
            is_tag_pre_sale = False
        )
        
        if discount_categ:
            percent = get_percent(discount_categ)
            sale = discount_categ

    if vendors and percent == 0:

        discount_all = Discount.objects.filter(
            vendor=vendors,
            group_supplier__isnull=True,
            category_supplier__isnull=True,
            category_supplier_all__isnull=True,
            is_tag_pre_sale = False
        )
        # скидка по всем вендору
        if discount_all:
            percent = get_percent(discount_all)
            sale = discount_all
            
    if percent == 0:

        discount_all = Discount.objects.filter(
            supplier=supplier,
            vendor__isnull=True,
            group_supplier__isnull=True,
            category_supplier__isnull=True,
            category_supplier_all__isnull=True,
            is_tag_pre_sale = False
        )
        # скидка по всем вендору
        if discount_all:
            percent = get_percent(discount_all)
            sale = discount_all
        # нет скидки
    
    motrum_price = rub_price_supplier - (rub_price_supplier / 100 * float(percent))
    # обрезать цены
    motrum_price = round(motrum_price, 2)

    return motrum_price, sale[0]


# перевод валютной цены в рубли
def get_price_supplier_rub(currency, vat, vat_includ, price_supplier):
    from apps.product.models import CurrencyRate

    if vat_includ == True:
        vat = 0
    if price_supplier is not None:
        if currency == "RUB":
            price_supplier_vat = price_supplier + (price_supplier / 100 * vat)
            return price_supplier_vat
        else:
            currency_rate_query = CurrencyRate.objects.filter(
                currency__words_code=currency
            ).latest("date")
            currency_rate = currency_rate_query.vunit_rate
            current_percent = CurrencyPercent.objects.filter().latest("id")

            price_supplier_vat = price_supplier + (price_supplier / 100 * vat)

            price_supplier_rub = (
                price_supplier_vat * currency_rate * current_percent.percent
            )

            return round(price_supplier_rub, 2)
    else:
        return None


# получение комплектности и расчет штук
def get_lot(lot, stock_supplier, lot_complect):
    from apps.product.models import Lot

    if lot == "base" or lot == "штука":
        lots = Lot.objects.get(name_shorts="шт")
        lot_stock = stock_supplier
        lot_complect = 1
    else:
        lots = Lot.objects.get(name=lot)
        lot_stock = stock_supplier * lot_complect
        lot_complect = lot_complect
    return (lots, lot_stock, lot_complect)


# остатки на складе мотрум
def get_lot_motrum():
    pass


# артикул мотрум
def create_article_motrum(supplier):
    from apps.product.models import Product

    supplier_int = str(supplier).zfill(3)

    try:
        prev_product = Product.objects.filter(supplier=supplier).latest("id")
        last_item_id = str(prev_product.article)[3:]
        last_item_id_int = int(last_item_id) + 1
        name = f"{supplier_int}{last_item_id_int}"
    except Product.DoesNotExist:
        prev_product = None

        name = f"{supplier_int}1"

    return name


# категории поставщика для товара
def get_category(supplier, vendor, category_name):
    from apps.supplier.models import (
        SupplierCategoryProduct,
        SupplierCategoryProductAll,
        SupplierGroupProduct,
    )

    try:
        item_category_all = SupplierCategoryProductAll.objects.filter(
            supplier=supplier, name=category_name
        )
        item_category = item_category_all[0].category_supplier
        item_group = item_category_all[0].group_supplier
    except SupplierCategoryProductAll.DoesNotExist:
        item_category = None
        item_group = None
        item_category_all = None

    return (item_category, item_group, item_category_all[0])


# категории поставщика промповер для товара
def get_category_prompower(supplier, vendor, category_name):
    from apps.supplier.models import (
        SupplierCategoryProduct,
        SupplierCategoryProductAll,
        SupplierGroupProduct,
    )

    try:
        category_all = SupplierCategoryProductAll.objects.get(
            supplier=supplier, vendor=vendor, article_name=category_name
        )
        groupe = category_all.group_supplier
        categ = category_all.category_supplier
    except SupplierCategoryProductAll.DoesNotExist:
        try:
            groupe = SupplierGroupProduct.objects.get(
                supplier=supplier, vendor=vendor, article_name=category_name
            )
            category_all = None

            categ = groupe.category_supplier
        except SupplierGroupProduct.DoesNotExist:
            try:
                categ = SupplierCategoryProduct.objects.get(
                    supplier=supplier, vendor=vendor, article_name=category_name
                )
                category_all = None
                groupe = None

            except SupplierGroupProduct.DoesNotExist:
                category_all = None
                groupe = None
                categ = None

    return (category_all, groupe, categ)


# ктегории поставщика для еиас
def get_category_emas(supplier, category_name):
    from apps.supplier.models import (
        SupplierCategoryProduct,
        SupplierCategoryProductAll,
        SupplierGroupProduct,
    )

    try:
        category_all = SupplierCategoryProductAll.objects.get(
            supplier=supplier, article_name=category_name
        )
        groupe = category_all.group_supplier
        categ = category_all.category_supplier
    except SupplierCategoryProductAll.DoesNotExist:
        try:
            groupe = SupplierGroupProduct.objects.get(
                supplier=supplier, article_name=category_name
            )
            category_all = None

            categ = groupe.category_supplier
        except SupplierGroupProduct.DoesNotExist:
            try:
                categ = SupplierCategoryProduct.objects.get(
                    supplier=supplier, article_name=category_name
                )
                category_all = None
                groupe = None

            except SupplierGroupProduct.DoesNotExist:
                category_all = None
                groupe = None
                categ = None
    return (category_all, groupe, categ)


# проверка есть ли путь и папка
def check_media_directory_exist(
    base_dir, base_dir_supplier, base_dir_vendor, base_dir_type_file, article_suppliers
):
    new_dir = "{0}/{1}/{2}/{3}/{4}/{5}".format(
        MEDIA_ROOT,
        base_dir,
        base_dir_supplier,
        base_dir_vendor,
        base_dir_type_file,
        article_suppliers,
    )
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)


# проверка директории для спецификаций
def check_spesc_directory_exist(
    base_dir,
):
    new_dir = "{0}/{1}".format(
        MEDIA_ROOT,
        base_dir,
    )

    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    return new_dir


# проверка директории для загрузки прайса из админки
def check_file_price_directory_exist(base_dir, base_dir_supplier):
    import shutil

    new_dir = "{0}/{1}/{2}".format(MEDIA_ROOT, base_dir, base_dir_supplier)

    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    else:
        shutil.rmtree(new_dir)

    return new_dir


# переименовывание изображений и документов по очереди
def create_name_file_downloading(article_suppliers, item_count):

    try:

        count = f"{item_count:05}"
        filename = "{0}_{1}".format(article_suppliers, count)
        return filename
    except item_count.DoesNotExist:
        return filename


def get_file_path(supplier, vendor, type_file, article_suppliers, item_count, place):
    base_dir = "products"
    base_dir_supplier = supplier
    base_dir_vendor = vendor
    base_dir_type_file = type_file
    filename = create_name_file_downloading(article_suppliers, item_count)

    check_media_directory_exist(
        base_dir,
        base_dir_supplier,
        base_dir_vendor,
        article_suppliers,
        base_dir_type_file,
    )
    if place == "utils":
        return "{0}/{1}/{2}/{3}/{4}".format(
            base_dir,
            base_dir_supplier,
            base_dir_vendor,
            article_suppliers,
            base_dir_type_file,
        )
    else:
        return "{0}/{1}/{2}/{3}/{4}/{5}".format(
            base_dir,
            base_dir_supplier,
            base_dir_vendor,
            article_suppliers,
            base_dir_type_file,
            filename,
        )


def save_file_product(link, image_path):
    r = requests.get(link, stream=True)
    with open(os.path.join(MEDIA_ROOT, image_path), "wb") as ofile:
        ofile.write(r.content)


def save_file_emas_product(link, image_path):

    out = f"{MEDIA_ROOT}/price/emas_site/{link}"
    in_out = f"{MEDIA_ROOT}/{image_path}"
    shutil.copy2(out, in_out)


# сохранение изображений и докуметов из админки и общее
def get_file_path_add(instance, filename):
    from apps.product.models import ProductDocument
    from apps.product.models import ProductImage

    s = str(instance.product.article_supplier)
    item_instanse_name = re.sub("[^A-Za-z0-9]", "", s)

    base_dir = "products"
    base_dir_supplier = instance.product.supplier.slug

    if instance.product.vendor:
        base_dir_vendor = instance.product.vendor.slug
    else:
        base_dir_vendor = ""

    images_last_list = filename.split(".")
    type_file = "." + images_last_list[-1]

    if isinstance(instance, ProductDocument):
        path_name = "document"
        try:
            images_last = ProductDocument.objects.filter(
                product=instance.product
            ).latest("id")
            item_count = ProductDocument.objects.filter(
                product=instance.product
            ).count()
        except ProductDocument.DoesNotExist:
            item_count = 1

        filenames = create_name_file_downloading(item_instanse_name, item_count)
        filename = f"{filenames}_{instance.type_doc}{type_file}"

    elif isinstance(instance, ProductImage):
        path_name = "img"
        try:
            images_last = ProductImage.objects.filter(product=instance.product).latest(
                "id"
            )
            item_count = ProductImage.objects.filter(product=instance.product).count()
        except ProductImage.DoesNotExist:
            item_count = 1

        filenames = create_name_file_downloading(item_instanse_name, item_count)

        filename = filenames + type_file

    check_media_directory_exist(
        base_dir,
        base_dir_supplier,
        base_dir_vendor,
        item_instanse_name,
        path_name,
    )
    return "{0}/{1}/{2}/{3}/{4}/{5}".format(

        base_dir,
        base_dir_supplier,
        base_dir_vendor,
        item_instanse_name,
        path_name,
        filename,
    )


# проверка есть ли такой тип лота шт комп
def lot_chek(lot):
    from apps.product.models import Lot

    try:
        lot_item = Lot.objects.get(name_shorts=lot)
    except Lot.DoesNotExist:
        lot_item = Lot.objects.create(name_shorts=lot, name=lot)

    return lot_item


# ответ по соединению с апи
def response_request(response, location):
    if response >= 200 and response <= 399:
        return True
    else:
        error = "file api"
        if response == 502:
            pass
            # error_alert(error, location, response)
        # else:
        #     error_alert(error, location, response)
        return False


# создание времени окончания спецификации
def create_time_stop_specification():
    from apps.core.models import CalendarHoliday

    year_date = datetime.datetime.now().year
    year = str(year_date)

    data_bd = CalendarHoliday.objects.get(year=year)
    data_bd_holidays = data_bd.json_date

    now = datetime.datetime.now()
    day_work = 3
    list_day = []
    for x in range(3):
        one_day = now + datetime.timedelta(days=x)
        list_day.append(one_day)

    for list_day_item in list_day:
        list_day_item_date = list_day_item.date()
        holidays_day = data_bd_holidays["holidays"].count(str(list_day_item_date))
        day_work = day_work + holidays_day

    three_days = datetime.timedelta(day_work)
    in_three_days = now + three_days
    data_stop = in_three_days.strftime("%Y-%m-%d")

    return data_stop

# получение категорий мотрум из категорий поставщика
def get_motrum_category(self):
    category_catalog = None
    group_catalog = None
    if self.category_supplier_all != None:
        category_catalog = self.category_supplier_all.category_catalog
        group_catalog = self.category_supplier_all.group_catalog

    if self.group_supplier != None:

        if category_catalog == None and group_catalog == None:
            category_catalog = self.group_supplier.category_catalog
            group_catalog = self.group_supplier.group_catalog


    if self.category_supplier != None:
        if category_catalog == None and group_catalog == None:
            category_catalog = self.category_supplier.category_catalog
            group_catalog = self.category_supplier.group_catalog


    return (category_catalog, group_catalog)


# сохранение фаилов прайс из админки
def get_file_price_path_add(instance, filename):
    if instance.slug == "delta":
        base_dir = "price"
        base_dir_supplier = instance.slug

        current_date = datetime.date.today().isoformat()

        new_dir = check_file_price_directory_exist(
            base_dir,
            base_dir_supplier,
        )
        random_number = random.randint(1000, 9999)

        file = "{0}/{1}/{2}_{3}".format(
            base_dir,
            base_dir_supplier,
            random_number,
            instance.file,
        )
        # print(filename + filetype)

        return file

    elif instance.slug == "optimus-drive":
        base_dir = "price"
        base_dir_supplier = instance.slug

        current_date = datetime.date.today().isoformat()

        new_dir = check_file_price_directory_exist(
            base_dir,
            base_dir_supplier,
        )
        random_number = random.randint(1000, 9999)

        file = "{0}/{1}/{2}_{3}".format(
            base_dir,
            base_dir_supplier,
            random_number,
            instance.file,
        )
        # print(filename + filetype)

        return file

    elif instance.slug == "emas":
        base_dir = "price"
        base_dir_supplier = instance.slug

        current_date = datetime.date.today().isoformat()

        new_dir = check_file_price_directory_exist(
            base_dir,
            base_dir_supplier,
        )
        random_number = random.randint(1000, 9999)

        file = "{0}/{1}/{2}_{3}".format(
            base_dir,
            base_dir_supplier,
            random_number,
            instance.file,
        )
        # print(filename + filetype)

        return file

    elif instance.slug == "avangard":
        base_dir = "price"
        base_dir_supplier = instance.slug

        current_date = datetime.date.today().isoformat()

        new_dir = check_file_price_directory_exist(
            base_dir,
            base_dir_supplier,
        )
        random_number = random.randint(1000, 9999)

        file = "{0}/{1}/{2}_{3}".format(
            base_dir,
            base_dir_supplier,
            random_number,
            instance.file,
        )

        return file


# проверка заполненны ли поля продукта если нет добавить значение
def save_update_product_attr(
    product,
    supplier,
    vendor,
    additional_article_supplier,
    category_supplier_all,
    group_supplier,
    category_supplier,
    description,
    name,
):
    if product.supplier == None or product.supplier == '':
        product.supplier = supplier

    if product.vendor == None or product.vendor == '':
        product.vendor = vendor

    if product.additional_article_supplier == None or product.additional_article_supplier == '':
        product.additional_article_supplier = additional_article_supplier

    if product.category_supplier_all == None or product.category_supplier_all == '':
        product.category_supplier_all = category_supplier_all

    if product.group_supplier == None or product.group_supplier == '':
        product.group_supplier = group_supplier

    if product.category_supplier == None or product.category_supplier == '':
        product.category_supplier = category_supplier

    if product.description == None or product.description == '':
        product.description = description

    if product.name == None or product.name == '':
        product.name = name
    
    product._change_reason = 'Автоматическое'
    product.save()
    # update_change_reason(product, "Автоматическое")


def save_specification(received_data):
    from apps.product.models import Price, Product
    from apps.specification.models import ProductSpecification, Specification
    from apps.specification.utils import crete_pdf_specification
    
    # сохранение спецификации
    id_bitrix = received_data["id_bitrix"]  # сюда распарсить значения с фронта
    admin_creator_id = received_data["admin_creator_id"]
    id_specification = received_data["id_specification"]
    is_pre_sale = received_data["is_pre_sale"]
    products = received_data["products"]
    print(received_data)
   

    try:
        specification = Specification.objects.get(id=id_specification)

        product_old = ProductSpecification.objects.filter(specification=specification)

        # удалить продукты если удалили из спецификации
        for product_item_for_old in product_old:
            item_id = product_item_for_old.id
            having_items = False
            for products_new in products:
                if products_new['product_specif_id'] != "None":
                   
                    if int(products_new['product_specif_id']) == item_id:
                        having_items = True
                 
            if having_items == False:
                product_item_for_old._change_reason = "Ручное"
                product_item_for_old.delete()
                
                
            having_items = False
            
            # for i, dic in enumerate(products):
            #     print(99999)
            #     print(dic["product_specif_id"] )
            #     print(item_id)
            #     if dic["product_specif_id"] == item_id:
            #         having_items = True
            #         print(having_items)

            # if having_items == False:
            #     print(product_item_for_old.id)
            #     product_item_for_old.delete()

    except Specification.DoesNotExist:
        specification = Specification(
            id_bitrix=id_bitrix, admin_creator_id=admin_creator_id
        )
        specification._change_reason = "Ручное"
        specification.save()

    # сохранение продуктов для спецификации
    # перебор продуктов и сохранение
    total_amount = 0
    currency_product = False
    for product_item in products:
      
        product = Product.objects.get(id=product_item["product_id"])
        price = Price.objects.get(prod=product)
        price_pre_sale = get_presale_discount(product)
        
        # если цена по запросу взять ее если нет взять цену из бд
        if product_item["price_exclusive"] == True:
            
            price_one_before = product_item["price_one"]
            price_one = product_item["price_one"]
        
            # оригинальная цена без примененой скидки
            if product_item["extra_discount"] != '0' and product_item["extra_discount"] != '':
                price_one =  price_one_before / (1 - float(product_item["extra_discount"]) /
                100)
                price_one = round(price_one, 2)

            price_motrum_all = get_price_motrum(
                price.prod.category_supplier,
                price.prod.group_supplier,
                price.prod.vendor,
                # price.rub_price_supplier,
                price_one,
                price.prod.category_supplier_all,
                price.prod.supplier,
            )
            price_one_motrum = price_motrum_all[0]
            sale = price_motrum_all[1]
            

        else:
            price_one = price.rub_price_supplier
            price_one_motrum = price.price_motrum 
            
        # если есть доп скидка отнять от цены поставщика
    
        if product_item["extra_discount"] != '0' and product_item["extra_discount"] != '':
            price_one = price_one - (
                price_one / 100 * float(product_item["extra_discount"])
            )
            price_one = round(price_one, 2)

        # если есть предоплата найти скидку по предоплате мотрум
        if is_pre_sale == True and price_pre_sale != False :
            persent_pre_sale = price_pre_sale.percent
            price_one_motrum = price_one_motrum - (price_one_motrum / 100 * float(persent_pre_sale))
            price_one_motrum = round(price_one_motrum, 2)
        
        price_all = float(price_one) * int(product_item["quantity"])
        price_all_motrum = float(price_one_motrum) * int(product_item["quantity"])
        
        if product_item["product_specif_id"] != "None":
            product_spes = ProductSpecification.objects.get(
                id=product_item["product_specif_id"],
            )
            
        else:  
            product_spes = ProductSpecification(
                specification=specification,
                product=product,
                # product_currency=price.currency,
                # price_exclusive=product_item["price_exclusive"],
            )
        product_spes.price_exclusive = product_item["price_exclusive"]       
        product_spes.product_currency = price.currency   
        product_spes.quantity = product_item["quantity"]
        product_spes.price_all = price_all
        product_spes.price_one = price_one
        if product_item["extra_discount"] != '0' and product_item["extra_discount"] != '':
            product_spes.extra_discount = product_item["extra_discount"]
        else:
             product_spes.extra_discount = None
        product_spes.price_one_motrum = price_one_motrum
        product_spes.price_all_motrum = price_all_motrum
        product_spes._change_reason = "Ручное"
        product_spes.save()    
        
        # try:
        #     product_spes = ProductSpecification.objects.get(
        #         id=product_item["product_specif_id"],
        #     )
        # except ProductSpecification.DoesNotExist:
        #     product_spes = ProductSpecification(
        #         specification=specification,
        #         product=product,
        #         product_currency=price.currency,
        #         price_exclusive=product_item["price_exclusive"],
        #     )
        # finally:
        #     product_spes.quantity = product_item["quantity"]
        #     product_spes.price_all = price_all
        #     product_spes.price_one = price_one
        #     product_spes.extra_discount = product_item["extra_discount"]
        #     product_spes.price_one_motrum = price_one_motrum
        #     product_spes.price_all_motrum = price_all_motrum
        #     product_spes.save()

        total_amount = total_amount + price_all

    # обновить спецификацию пдф
    specification.total_amount = total_amount
    specification._change_reason = "Ручное"             
    specification.save()
    pdf = crete_pdf_specification(specification.id)
    specification.file = pdf        
    specification.save()
    # Specification.objects.filter(id=specification.id).update(file=pdf)

    return received_data


def get_presale_discount(product):
    from apps.supplier.models import Discount
    
    supplier = product.supplier
    try:
        discount = Discount.objects.get(supplier=supplier,is_tag_pre_sale=True)
        return discount
    except  Discount.DoesNotExist:
        return False