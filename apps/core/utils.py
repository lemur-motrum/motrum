# расчет цены
import shutil
import requests
import hashlib
import os


from apps.supplier.models import Discount, SupplierCategoryProductAll
from django.conf import settings
from project.settings import MEDIA_ROOT


# расчет цены для мотрум
# TODO: переписать на трае ексепт
def get_price_motrum(item_category, item_group, vendors, rub_price_supplier):
    motrum_price = rub_price_supplier
    percent = 0
    sale = None

    # получение процента функция
    def get_percent(item):
        for i in item:
            return i.percent

    # скидка по группе
    if item_group:
        discount_group = Discount.objects.filter(group_supplier=item_group.id)
        print(discount_group, "!!!!!!!!!!!!!!!")
        if discount_group:
            percent = get_percent(discount_group)
            sale = discount_group
    # скидка по категории
    elif item_category:
        discount_categ = Discount.objects.filter(
            category_supplier=item_category.id,
            group_supplier__isnull=True,
        )
        if discount_categ:
            percent = get_percent(discount_categ)
            sale = discount_categ

    else:
        discount_all = Discount.objects.filter(
            vendor=vendors, group_supplier__isnull=True, category_supplier__isnull=True
        )

        # скидка по всем вендору
        if discount_all:
            percent = get_percent(discount_all)
            sale = discount_all
        # нет скидки

    motrum_price = rub_price_supplier - (rub_price_supplier / 100 * int(percent))
    # TODO обрезать цены

    return motrum_price, sale


def get_price_supplier_rub(currency, vat, vat_includ, price_supplier):
    if vat_includ == True:
        vat = 0

    if currency == "RUB":
        price_supplier_vat = price_supplier + (price_supplier / 100 * vat)
        return price_supplier_vat
    else:
        val = 1
        price_supplier_vat = price_supplier + (price_supplier / 100 * vat)
        price_supplier_rub = price_supplier_vat * val * 1.03
        return price_supplier_rub


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
def create_article_motrum(supplier, vendor):
    from apps.product.models import Product

    try:
        prev_product = Product.objects.filter(supplier=supplier).latest("id")
        last_item_id = int(prev_product.article) + 1
        name = str(last_item_id)
    except Product.DoesNotExist:
        prev_product = None
        name = f"{supplier}{vendor}1"
    return name


# категории дял товара
def get_category(supplier, vendor, category_name):
    try:
        item_category_all = SupplierCategoryProductAll.objects.get(
            supplier=supplier, name=category_name
    )
        item_category = item_category_all.category_supplier
        item_group = item_category_all.group_supplier
    except SupplierCategoryProductAll.DoesNotExist:
        item_category = None
        item_group =None
    
    
    print(item_category, "item_category")
    print(item_group, "item_group")
    print("/////////")
    return (item_category, item_group)


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


def save_file_product(link, image_path, filename, filetype):
    r = requests.get(link, stream=True)
    print(filename + filetype)
    with open(os.path.join(MEDIA_ROOT, image_path, filename + filetype), "wb") as ofile:
        ofile.write(r.content)


def get_file_path_add(instance, filename):

    from apps.product.models import ProductImage

    base_dir = "products"
    base_dir_supplier = instance.product.supplier.slug
    base_dir_vendor = instance.product.vendor.slug
    images_last_list = filename.split(".")
    type_file = "." + images_last_list[-1]
    if images_last_list[-1] == "jpg" or images_last_list[-1] == "png":
        path_name = "img"
    else:
        path_name = "document"

    try:
        images_last = ProductImage.objects.filter(product=instance.product).latest("id")
        item_count = ProductImage.objects.filter(product=instance.product).count()

    except ProductImage.DoesNotExist:
        item_count = 1

    filenames = create_name_file_downloading(
        instance.product.article_supplier, item_count
    )

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
        filenames + type_file,
    )
