# расчет цены
import datetime
import random
import shutil
import requests
import hashlib
import os
import traceback


# from apps import supplier
from apps.core.models import Currency, CurrencyPercent
from apps.logs.utils import error_alert
from django.conf import settings
from apps.supplier.get_utils.delta import add_file_delta
from project.settings import MEDIA_ROOT


# цена мотрум со скидкой
def get_price_motrum(
    item_category, item_group, vendors, rub_price_supplier, all_item_group
):
    from apps.supplier.models import (
        Discount,
    )

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
            # vendor=vendors,
            # group_supplier__isnull=True,
            # category_supplier__isnull=True,
        )

        if discount_all_group:
            percent = get_percent(discount_all_group)
            sale = discount_all_group

        # скидка по группе

    if item_group and percent == 0:

        discount_group = Discount.objects.filter(group_supplier=item_group.id)

        if discount_group:
            percent = get_percent(discount_group)
            sale = discount_group
            # if percent != 0

    # скидка по категории
    if item_category and percent == 0:

        discount_categ = Discount.objects.filter(
            category_supplier_id=item_category.id,
            # group_supplier__isnull=True,
        )

        if discount_categ:
            percent = get_percent(discount_categ)
            sale = discount_categ

    if percent == 0:

        discount_all = Discount.objects.filter(
            vendor=vendors,
            group_supplier__isnull=True,
            category_supplier__isnull=True,
            category_supplier_all__isnull=True,
        )
        # скидка по всем вендору
        if discount_all:
            percent = get_percent(discount_all)
            sale = discount_all

        # нет скидки

    motrum_price = rub_price_supplier - (rub_price_supplier / 100 * float(percent))
    # TODO обрезать цены
    motrum_price = round(motrum_price, 2)
    # for sal in sales:
    #             sale = sal
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


# сохранение изображений и докуметов из админки и общее
def get_file_path_add(instance, filename):
    from apps.product.models import ProductDocument
    from apps.product.models import ProductImage

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
        # print(instance.type_doc)
        # print(item_count)
        print(instance)
        print(instance.type_doc)
        filenames = create_name_file_downloading(
            instance.product.article_supplier, item_count
        )
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
        # print(item_count)
        filenames = create_name_file_downloading(
            instance.product.article_supplier, item_count
        )

        filename = filenames + type_file

    check_media_directory_exist(
        base_dir,
        base_dir_supplier,
        base_dir_vendor,
        instance.product.article_supplier,
        path_name,
    )
    return "{0}/{1}/{2}/{3}/{4}/{5}".format(
        base_dir,
        base_dir_supplier,
        base_dir_vendor,
        instance.product.article_supplier,
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


def response_request(response, location):
    if response >= 200 and response <= 399:
        return True
    else:
        error = "file api"
        error_alert(error, location, response)
        return False


# создание времени окончания спецификации
def create_time():
    now = datetime.datetime.now()
    three_days = datetime.timedelta(3)
    in_three_days = now + three_days
    data = in_three_days.strftime("%Y-%m-%d")

    return data


# емеил
def send_email_error():
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import smtplib

    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.starttls()
    smtp_server.login("steisysi@gmail.com", "")

    # Создание объекта сообщения
    msg = MIMEMultipart()

    # Настройка параметров сообщения
    msg["From"] = "steisysi@gmail.com"
    msg["To"] = "steisysi@gmail.com"
    msg["Subject"] = "Тестовое письмо 📧"

    # Добавление текста в сообщение
    text = "Привет! Это тестовое письмо, отправленное с помощью Python 😊"
    msg.attach(MIMEText(text, "plain"))

    # Отправка письма
    smtp_server.sendmail("steisysi@gmail.com", "steisysi@gmail.com", msg.as_string())

    # Закрытие соединения
    smtp_server.quit()


# получение категорий мотрум из категорий поставщика
def get_motrum_category(self):
    category_catalog = None
    group_catalog = None

    if self.category_supplier_all != None:
        category_catalog = self.category_supplier_all.category_catalog
        group_catalog = self.category_supplier_all.group_catalog
        return (category_catalog, group_catalog)

    if self.group_supplier != None:
        category_catalog = self.group_supplier.category_catalog
        group_catalog = self.group_supplier.group_catalog
        return (category_catalog, group_catalog)

    if self.category_supplier != None:
        category_catalog = self.category_supplier.category_catalog
        group_catalog = self.category_supplier.group_catalog
        return (category_catalog, group_catalog)

    return (category_catalog, group_catalog)


# сохранение фаилов прайсовы из админки
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

    elif instance.slug == "Optimus drive":
        pass
