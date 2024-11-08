# расчет цены
import datetime
import random
import re
import shutil
import requests
import hashlib
import os
import traceback
from django.core.cache import cache
import traceback


from apps.core.models import Currency, CurrencyPercent, Vat
from apps.logs.utils import error_alert



from project.settings import MEDIA_ROOT
from simple_history.utils import update_change_reason


# цена мотрум со скидкой
def get_price_motrum(
    item_category, item_group, vendors, rub_price_supplier, all_item_group, supplier
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
            is_tag_pre_sale=False,
        )

        if discount_all_group:
            percent = get_percent(discount_all_group)
            sale = discount_all_group

        # скидка по группе

    if item_group and percent == 0:

        discount_group = Discount.objects.filter(
            category_supplier_all__isnull=True,
            group_supplier=item_group.id,
            is_tag_pre_sale=False,
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
            is_tag_pre_sale=False,
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
            is_tag_pre_sale=False,
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
            is_tag_pre_sale=False,
        )
        # скидка по всем вендору
        if discount_all:
            percent = get_percent(discount_all)
            sale = discount_all
        # нет скидки
    if rub_price_supplier:

        motrum_price = rub_price_supplier - (rub_price_supplier / 100 * float(percent))
        # обрезать цены
        motrum_price = round(motrum_price, 2)
    else:
        motrum_price = None

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
    doc = "document"
    new_dir = "{0}/{1}/{2}".format(
        MEDIA_ROOT,
        "documents",
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
    from pytils import translit

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


def get_file_path_add_more_doc(product, type_doc, filename):

    from apps.product.models import ProductDocument
    from apps.product.models import ProductImage

    from pytils import translit

    base_dir = "products"
    path_name = "document_group"
    base_dir_supplier = product.supplier.slug
    if product.vendor:
        base_dir_vendor = product.vendor.slug
    else:
        base_dir_vendor = "vendor-name"

    if product.category:
        base_dir_vendor = product.category.slug
    else:
        base_dir_vendor = "category-name"

    type_doc = type_doc

    slug_text = str(filename)
    regex = r"[^A-Za-z0-9,А-ЯЁа-яё, ,-.]"
    slugish = re.sub(regex, "", slug_text)
    slugish = translit.translify(slugish)

    # link_file = f"{new_dir}/{slugish}"
    new_dir = "{0}/{1}/{2}/{3}/{4}/{5}".format(
        MEDIA_ROOT,
        base_dir,
        base_dir_supplier,
        base_dir_vendor,
        path_name,
        type_doc,
    )
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    link = "{0}/{1}/{2}/{3}/{4}".format(
        base_dir,
        base_dir_supplier,
        base_dir_vendor,
        path_name,
        type_doc,
    )

    return (link, slugish)


# сохранение изображений и докуметов из админки и общее
def doc_file_mass_upload(instance, filename):
    from apps.product.models import ProductDocument

    base_dir = "products"
    path_name = "document_group"
    base_dir_supplier = instance.product.supplier.slug
    base_dir_vendor = instance.product.vendor.slug
    group_name = instance.product.category_supplier.slug

    s = str(instance.product.article_supplier)
    item_instanse_name = re.sub("[^A-Za-z0-9]", "", s)
    new_dir = "{0}/{1}/{2}/{3}/{4}/{5}".format(
        MEDIA_ROOT,
        base_dir,
        base_dir_supplier,
        base_dir_vendor,
        path_name,
        group_name,
    )
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    dir_no_path = "{0}/{1}/{2}/{3}/{4}".format(
        base_dir,
        base_dir_supplier,
        base_dir_vendor,
        path_name,
        group_name,
    )
    # base_dir = "products"
    # base_dir_supplier = instance.product.supplier.slug

    # if instance.product.vendor:
    #     base_dir_vendor = instance.product.vendor.slug
    # else:
    #     base_dir_vendor = ""

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

    # check_media_directory_exist(
    #     base_dir,
    #     base_dir_supplier,
    #     base_dir_vendor,
    #     item_instanse_name,
    #     path_name,
    # )
    return "{0}/{1}/{2}/{3}/{4}/{5}".format(
        base_dir,
        base_dir_supplier,
        base_dir_vendor,
        item_instanse_name,
        path_name,
        filename,
    )


def get_file_path_add_motrum_base(instance, filename):
    from pytils import translit

    new_dir = "{0}/{1}".format(MEDIA_ROOT, "documents")
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    slug_text = str(filename)
    regex = r"[^A-Za-z0-9,А-ЯЁа-яё, ,-.]"
    slugish = re.sub(regex, "", slug_text)
    slugish = translit.translify(slugish)

    link_file = f"{new_dir}/{slugish}"

    return "{0}/{1}".format(
        "documents",
        f"{slugish}",
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

    day_need = 1
    i = 0
    while day_need <= 3:
        i += 1
        date = now + datetime.timedelta(days=i)

        if date.year > year_date:
            data_bd = CalendarHoliday.objects.get(year=date.year)
            data_bd_holidays = data_bd.json_date
            holidays_day_need = data_bd_holidays["holidays"].count(str(date.date()))

            if "nowork" in data_bd_holidays and holidays_day_need == 0:
                holidays_day_need_nowork = data_bd_holidays["nowork"].count(
                    str(date.date())
                )
                holidays_day_need += holidays_day_need_nowork
        else:
            holidays_day_need = data_bd_holidays["holidays"].count(str(date.date()))

            if "nowork" in data_bd_holidays and holidays_day_need == 0:
                holidays_day_need_nowork = data_bd_holidays["nowork"].count(
                    str(date.date())
                )
                holidays_day_need += holidays_day_need_nowork

        if holidays_day_need == 0:

            day_need += 1

    three_days = datetime.timedelta(i)
    in_three_days = now + three_days
    data_stop = in_three_days.strftime("%Y-%m-%d")

    return data_stop
    # year_date = datetime.datetime.now().year
    # year = str(year_date)

    # data_bd = CalendarHoliday.objects.get(year=year)
    # data_bd_holidays = data_bd.json_date

    # now = datetime.datetime.now()
    # day_work = 3
    # list_day = []
    # for x in range(3):
    #     one_day = now + datetime.timedelta(days=x)
    #     list_day.append(one_day)

    # for list_day_item in list_day:
    #     list_day_item_date = list_day_item.date()
    #     holidays_day = data_bd_holidays["holidays"].count(str(list_day_item_date))
    #     day_work = day_work + holidays_day

    # three_days = datetime.timedelta(day_work)
    # in_three_days = now + three_days
    # data_stop = in_three_days.strftime("%Y-%m-%d")

    # return data_stop


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

    try:
        if product.supplier == None or product.supplier == "":
            product.supplier = supplier

        if product.vendor == None or product.vendor == "":
            product.vendor = vendor
        if product.vendor == None or product.vendor == "":
            product.vendor = vendor

        if (
            product.additional_article_supplier == None
            or product.additional_article_supplier == ""
        ):
            product.additional_article_supplier = additional_article_supplier
        if (
            product.additional_article_supplier == None
            or product.additional_article_supplier == ""
        ):
            product.additional_article_supplier = additional_article_supplier

        if product.category_supplier_all == None or product.category_supplier_all == "":
            product.category_supplier_all = category_supplier_all
        if product.category_supplier_all == None or product.category_supplier_all == "":
            product.category_supplier_all = category_supplier_all

        if product.group_supplier == None or product.group_supplier == "":
            product.group_supplier = group_supplier
        if product.group_supplier == None or product.group_supplier == "":
            product.group_supplier = group_supplier

        if product.category_supplier == None or product.category_supplier == "":
            product.category_supplier = category_supplier
        if product.category_supplier == None or product.category_supplier == "":
            product.category_supplier = category_supplier

        if product.description == None or product.description == "":
            product.description = description
        if product.description == None or product.description == "":
            product.description = description

        if product.name == None or product.name == "":
            product.name = name
        if product.name == None or product.name == "":
            product.name = name

        product._change_reason = "Автоматическое"
        product.save()
    except Exception as e:
        print(e)
        error = "file_api_error"
        location = "Загрузка фаилов IEK"
        info = f"ошибка при чтении товара артикул ИЗ ФУНКЦИИ save_update_product_attr: {name}. Тип ошибки:{e}"
        e = error_alert(error, location, info)
    # update_change_reason(product, "Автоматическое")


def save_specification(
    received_data,
    pre_sale,
    request,
    motrum_requisites,
    account_requisites,
    requisites,
    id_bitrix,
    type_delivery,
    post_update,
    specification_name,
):
    from apps.product.models import Price, Product
    from apps.specification.models import ProductSpecification, Specification
    from apps.specification.utils import crete_pdf_specification
    from apps.product.models import ProductCart
    from apps.core.utils import create_time_stop_specification

    # try:
    print("save_specification",specification_name)
    # сохранение спецификации
    id_bitrix = received_data["id_bitrix"]  # сюда распарсить значения с фронта
    admin_creator_id = received_data["admin_creator_id"]
    id_specification = received_data["id_specification"]
    specification_comment = received_data["comment"]
    date_delivery_all = received_data["date_delivery"]
    products = received_data["products"]
    id_cart = received_data["id_cart"]

    # первичное создание/взятие спецификации
    try:
        specification = Specification.objects.get(id=id_specification)
        if post_update:
            pass
        else:

            data_stop = create_time_stop_specification()
            specification.date_stop = data_stop
            specification.tag_stop = True

        # удалить продукты если удалили из спецификации
        product_old = ProductSpecification.objects.filter(specification=specification)
        for product_item_for_old in product_old:
            item_id = product_item_for_old.id
            having_items = False
            for products_new in products:
                if (
                    products_new["product_specif_id"] != "None"
                    and products_new["product_specif_id"] != None
                ):

                    if int(products_new["product_specif_id"]) == item_id:
                        having_items = True

            if having_items == False:

                specification._change_reason = "Ручное"
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
            id_bitrix=id_bitrix, admin_creator_id=admin_creator_id, cart_id=id_cart
        )
        if specification_name:
            specification.number = specification_name
        specification.skip_history_when_saving = True
        data_stop = create_time_stop_specification()
        specification.date_stop = data_stop
        specification.tag_stop = True
        # specification._change_reason = "Ручное"
        specification.save()

    # сохранение продуктов для спецификации
    # перебор продуктов и сохранение
    total_amount = 0.00
    date_ship = datetime.date.today().isoformat()
    currency_product = False

    for product_item in products:
        print(products)
        # продукты которые есть в окт
        if product_item["product_id"] != 0:
            product = Product.objects.get(id=product_item["product_id"])
            price = Price.objects.get(prod=product)
            # если цена по запросу взять ее если нет взять цену из бд
            if (
                product_item["price_exclusive"] != "0"
                and product_item["price_exclusive"] != ""
                and product_item["price_exclusive"] != 0
            ):

                price_one_before = product_item["price_one"]
                price_one = product_item["price_one"]

                # оригинальная цена без примененой скидки
                # if (
                #     product_item["extra_discount"] != "0"
                #     and product_item["extra_discount"] != ""
                # ):
                #     price_one = price_one_before / (
                #         1 - float(product_item["extra_discount"]) / 100
                #     )
                #     price_one = round(price_one, 2)
                #     print(price_one)
                print(4444444)
                if price.in_auto_sale:
                    price_motrum_all = get_price_motrum(
                        price.prod.category_supplier,
                        price.prod.group_supplier,
                        price.prod.vendor,
                        # price.rub_price_supplier,
                        price_one,
                        price.prod.category_supplier_all,
                        price.prod.supplier,
                    )
                    print(123123123)
                    price_one_motrum = price_motrum_all[0]
                    sale = price_motrum_all[1]
                else:
                    price_one = price.rub_price_supplier
                    price_one_motrum = price.price_motrum

            else:
                print(77777777)
                price_one = price.rub_price_supplier
                price_one_motrum = price.price_motrum

            # если есть доп скидка отнять от цены поставщика

            if (
                product_item["extra_discount"] != "0"
                and product_item["extra_discount"] != ""
                and product_item["extra_discount"] != 0
            ):
                # если есть предоплата найти скидку по предоплате мотрум
                persent_pre_sale = 0
                if pre_sale:
                    price_pre_sale = get_presale_discount(product)
                    if price_pre_sale:
                        persent_pre_sale = price_pre_sale.percent

                persent_sale = float(product_item["extra_discount"])
                persent_sale = float(persent_sale) + float(persent_pre_sale)

                price_one_sale = price_one - (price_one / 100 * persent_sale)
                price_one = round(price_one_sale, 2)

            # # если есть предоплата найти скидку по предоплате мотрум
            # if pre_sale:
            #     price_pre_sale = get_presale_discount(product)
            #     if price_pre_sale:
            #         persent_pre_sale = price_pre_sale.percent
            #         price_one_motrum = price_one_motrum - (
            #             price_one_motrum / 100 * float(persent_pre_sale)
            #         )
            #         price_one_motrum = round(price_one_motrum, 2)

            price_all = float(price_one) * int(product_item["quantity"])
            price_all = round(price_all, 2)
            price_all_motrum = float(price_one_motrum) * int(product_item["quantity"])
            price_all_motrum = round(price_all_motrum, 2)

            # выбор продукт из спецификации или заспись нового
            if (
                product_item["product_specif_id"] != "None"
                and product_item["product_specif_id"] != None
            ):
                product_spes = ProductSpecification.objects.get(
                    id=product_item["product_specif_id"],
                )

            else:
                product_spes = ProductSpecification(
                    specification=specification,
                    product=product,
                )
            product_spes.price_exclusive = product_item["price_exclusive"]
            product_spes.product_currency = price.currency
            product_spes.quantity = product_item["quantity"]
            product_spes.price_all = price_all

            product_spes.price_one = price_one
            if (
                product_item["extra_discount"] != "0"
                and product_item["extra_discount"] != ""
                and product_item["extra_discount"] != 0
            ):
                product_spes.extra_discount = product_item["extra_discount"]
            else:
                product_spes.extra_discount = None

            product_spes.price_one_motrum = price_one_motrum
            product_spes.price_all_motrum = price_all_motrum
            product_spes._change_reason = "Ручное"
            product_spes.comment = product_item["comment"]

            # запись дат
            date_delivery = product_item["date_delivery"]
            if date_delivery != "":
                product_spes.date_delivery = datetime.datetime.strptime(
                    date_delivery, "%Y-%m-%d"
                )
                product_spes.date_delivery = date_delivery

            product_spes.save()

            total_amount = total_amount + price_all

        # продукты без записи в окт
        else:
            print(33333333333333)
            price_one = product_item["price_one"]
            price_one_original_new = price_one
            if product_item["sale_motrum"]:
                motrum_sale = product_item["sale_motrum"]
                motrum_sale = motrum_sale.replace('.', '')
                motrum_sale = motrum_sale.replace(',', '.')
                motrum_sale = float(motrum_sale)
            else:
                motrum_sale = 0.00
            price_one_motrum = price_one - (price_one / 100 * motrum_sale) 
            price_all_motrum = float(price_one_motrum) * int(product_item["quantity"])
            price_all_motrum = round(price_all_motrum, 2) 

            if (
                product_item["extra_discount"] != "0"
                and product_item["extra_discount"] != ""
                and product_item["extra_discount"] != 0
            ):

                persent_sale = float(product_item["extra_discount"])

                price_one_sale = price_one - (price_one / 100 * persent_sale)
                price_one = round(price_one_sale, 2)
            
                
           
            price_all = float(price_one) * int(product_item["quantity"])
            price_all = round(price_all, 2)

            currency = Currency.objects.get(words_code="RUB")

            if (
                product_item["product_specif_id"] != "None"
                and product_item["product_specif_id"] != None
            ):
                product_spes = ProductSpecification.objects.get(
                    id=product_item["product_specif_id"],
                )

            else:
                product_spes = ProductSpecification(
                    specification=specification,
                    product=None,
                )
            
            
            
            if (
                product_item["extra_discount"] != "0"
                and product_item["extra_discount"] != ""
                and product_item["extra_discount"] != 0
            ):
                product_spes.extra_discount = product_item["extra_discount"]
            else:
                product_spes.extra_discount = None
            product_spes.price_exclusive = product_item["price_exclusive"]
            product_spes.product_currency = currency
            product_spes.quantity = product_item["quantity"]
            product_spes.price_all = price_all
            product_spes.price_one = price_one
            product_spes.price_one_original_new = price_one_original_new
            product_spes.sale_motrum = motrum_sale
            product_spes.price_one_motrum = price_one_motrum
            product_spes.price_all_motrum = price_all_motrum
            product_spes.product_new = product_item["product_name_new"]
            product_spes.product_new_article = product_item["product_new_article"]
            product_spes._change_reason = "Ручное"
            product_spes.comment = product_item["comment"]
            # product_spes.product_in_cart =
            date_delivery = product_item["date_delivery"]
            if date_delivery != "":
                product_spes.date_delivery = datetime.datetime.strptime(
                    date_delivery, "%Y-%m-%d"
                )
                product_spes.date_delivery = date_delivery
            product_spes.save()
            print(product_spes)

            total_amount = total_amount + price_all

    # обновить спецификацию пдф
    total_amount = round(total_amount, 2)
    specification.total_amount = total_amount
    specification.comment = specification_comment
    specification.date_delivery = date_delivery_all
    specification.id_bitrix = id_bitrix
    specification._change_reason = "Ручное"

    specification.save()
    if specification_name:
        pdf = crete_pdf_specification(
            specification.id,
            requisites,
            account_requisites,
            request,
            motrum_requisites,
            date_delivery_all,
            type_delivery,
            post_update,
            specification_name,
        )

        if pdf:
            specification.file = pdf
            specification._change_reason = "Ручное"

            specification.save()

    return specification

    # except Exception as e:
    #     # product_spes = ProductSpecification.objects.filter(
    #     #     specification=specification,
    #     # )
    #     # if product_spes:
    #     #     for prod in product_spes:
    #     #         prod.delete()
    #     # else:
    #     #     specification.delete()

    #     error = "error"
    #     location = "Сохранение спецификации админам окт"
    #     info = f"Сохранение спецификации админам окт ошибка {e}"
    #     e = error_alert(error, location, info)

    #     return None


def get_presale_discount(product):
    from apps.supplier.models import Discount

    supplier = product.supplier
    try:
        discount = Discount.objects.get(supplier=supplier, is_tag_pre_sale=True)
        return discount
    except Discount.DoesNotExist:
        return False


def transform_date(date):

    months = [
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря",
    ]
    (
        year,
        month,
        day,
    ) = date.split("-")
    return f"{day} {months[int(month) - 1]} {year} г."


def rub_words(n):

    n = str(n)

    if n[-2:] in ("11", "12", "13", "14"):
        return f"рублей"
        # print(n, 'копеек')
    elif n[-1] == "1":
        return f"рубль"
    elif n[-1] in ("2", "3", "4"):
        return f"рубля"
        # print(n, 'копейки')
    else:
        return f"рублей"
        # print(n, 'копеек')


def pens_words(n):

    if n[-2:] in ("11", "12", "13", "14"):
        return f"копеек"

    elif n[-1] == "1":
        return f"копейка"

    elif n[-1] in ("2", "3", "4"):
        return f"копейки"

    else:
        return f"копеек"


# общая функция кешировани
def loc_mem_cache(key, function, timeout=300):
    cache_data = cache.get(key)
    if not cache_data:
        cache_data = function()
        cache.set(key, cache_data, timeout)
    return cache_data


def save_new_product_okt(product_new):
    from apps.product.models import Product,Price,Lot,Stock
    from apps.supplier.models import Supplier, Vendor

    if product_new.vendor:
        vendor = product_new.vendor
        supplier = vendor.supplier
    else:
        vendor = Vendor.objects.get("drugoe")
        supplier = Supplier.objects.get("drugoe")

    product = Product(
        supplier=supplier, vendor=vendor, article_supplier=product_new.article_supplier,name=product_new.name,in_view_website=False
    )
    product.save()
    update_change_reason(product, "Автоматическое")
    
    currency = Currency.objects.get(words_code="RUB")
    vat = Vat.objects.get(name=20)
    
    price = Price(prod=product,currency=currency,vat=vat,extra_price=True,in_auto_sale=False)
    price.save()
    update_change_reason(price, "Автоматическое")
    
    lot_auto = Lot.objects.get(name_shorts="шт")
    product_stock = Stock(
        prod=product,
        lot=lot_auto,
    )
    product_stock.save()

# from django.utils.http import url_has_allowed_host_and_scheme
# import urllib


#  def orders_cache():
#             def cache_function():
#                 orders = (
#                     Order.objects.filter(client=client)
#                     .select_related(
#                         "specification",
#                         "cart",
#                         "requisites",
#                         "account_requisites",
#                     )
#                     .prefetch_related(
#                         Prefetch(
#                             "notification_set",
#                             queryset=Notification.objects.filter(
#                                 type_notification="STATUS_ORDERING", is_viewed=False
#                             ),
#                             to_attr="filtered_notification_items",
#                         )
#                     )
#                     .prefetch_related(
#                         Prefetch("specification__productspecification_set")
#                     )
#                     .prefetch_related(
#                         Prefetch("specification__productspecification_set__product")
#                     )
#                     .prefetch_related(
#                         Prefetch(
#                             "specification__productspecification_set__product__stock"
#                         )
#                     )
#                     .annotate(
#                         notification_count=Count(
#                             "notification",
#                             filter=Q(
#                                 notification__is_viewed=True,
#                                 notification__type_notification="STATUS_ORDERING",
#                             ),
#                         )
#                     )

#                 )
#                 return orders

#             return loc_mem_cache("orders_lk", cache_function, 200)

#         orders = orders_cache()
#         orders = orders.order_by(sorting, "-id")[count : count + count_last]
