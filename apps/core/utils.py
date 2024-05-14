# расчет цены
import shutil
import requests
import hashlib
import os
from apps.product.models import Lot, Product, ProductImage
from apps.supplier.models import Discount, SupplierCategoryProductAll
from django.conf import settings
from project.settings import MEDIA_ROOT


# расчет цены для мотрум
def get_price_motrum(item_category, item_group, vendors, rub_price_supplier):
    discount_group = Discount.objects.filter(group_catalog=item_group.id).values(
        "percent"
    )

    discount_categ = Discount.objects.filter(
        category_catalog=item_category.id,
        group_catalog__isnull=True,
    )
    discount_all = Discount.objects.filter(
        vendor=vendors, group_catalog__isnull=True, category_catalog__isnull=True
    )

    def get_percent(item):
        for i in item:
            return i.percent

    motrum_price = rub_price_supplier
    if discount_group:
        percent = get_percent(discount_group)

    elif discount_categ:
        percent = get_percent(discount_categ)

    elif discount_all:
        percent = get_percent(discount_all)
    else:
        percent = 0

    motrum_price = rub_price_supplier - (rub_price_supplier / 100 * int(percent))
    # TODO обрезать цены

    return motrum_price


# получение комплектности и расчет штук
def get_lot(lot, stock_supplier):

    if lot == "base":
        lots = Lot.objects.get(name_shorts="шт")
        lot_complect = 1
        lot_stock = stock_supplier
    else:
        pass

    return (lots, lot_complect, lot_stock)


# остатки на складе мотрум
def get_lot_motrum():
    pass


# артикул мотрум
def create_article_motrum(supplier, vendor):
    if Product.objects.filter(supplier=supplier).exists():
        # если есть товары вендора
        last_item = Product.objects.filter(supplier=supplier).latest("id")

        last_item_id = int(last_item.article) + 1

        name = str(last_item_id)
    else:
        # если нет товаров вендора
        name = f"{supplier}{vendor}1"

    return name


def get_price_all():
    pass


# категории дял товара
def get_category(supplier, category_name):
    item_category_all = SupplierCategoryProductAll.objects.get(
        supplier=supplier, name=category_name
    )
    item_category = item_category_all.category_catalog
    item_group = item_category_all.group_catalog
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
    count = f"{item_count:05}"
    filename = "{0}_{1}".format(article_suppliers, count)
    return filename


def get_file_path(
    base_dir, supplier, vendor, type_file, article_suppliers, item_count, place
):
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


def save_file_product(link, image_path, filename):
    r = requests.get(link, stream=True)

    with open(os.path.join(MEDIA_ROOT, image_path, filename + ".jpg"), "wb") as ofile:
        ofile.write(r.content)


# def save_image(product_id):
#     images = ProductImage.objects.filter(product=product_id).exists()
#     if images:
