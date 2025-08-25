from apps.product.models import Product
import traceback
from apps.logs.utils import error_alert


def export_all_prod_for_1c():
    import openpyxl as openxl
    from project.settings import MEDIA_ROOT
    import os
    try:
        products = Product.objects.filter(category__isnull=True
        ).order_by("vendor")[:100]
        
        title = [
            "Артикул мотрум",
            "Поставщик",
            "Производитель",
            "Артикул поставщика",
            "Название",
            "Описание товара",
            "Категории товара от поставщиков",
            "Группа товара от поставщиков",
            "Подгруппа категории товара от поставщиков",
            "Видимость на сайте",
            "КАТЕГОРИЯ МОТРУМ",
            "ГРУППА МОТРУМ",
        ]

        wb = openxl.Workbook()
        ws = wb.active
        ws.append(title)

        for product in products:
            
            article_motrum = getattr(product, "article", "")
            print(article_motrum)
            supplier = getattr(product.supplier, "name", "") if product.supplier else ""
            vendor = getattr(product.vendor, "name", "") if product.vendor else ""
            article_vendor = getattr(product, "article_supplier", "")
            name = getattr(product, "name", "")
            description = getattr(product, "description", "")
            category_supplier = getattr(product.category_supplier, "name", "") if product.category_supplier else ""
            group_supplier = getattr(product.group_supplier, "name", "") if product.group_supplier else ""
            category_supplier_all = getattr(product.category_supplier_all, "name", "") if product.category_supplier_all else ""
            ws.append([
                article_motrum,
                supplier,
                vendor,
                article_vendor,
                name,
                description,
                category_supplier,
                group_supplier,
                category_supplier_all
            ])

        file_path = os.path.join(MEDIA_ROOT, "all_none_categ_nomenk.xlsx")
        wb.save(file_path)
    except Exception as e:
        print(e)
        tr = traceback.format_exc()
        error = "file_error"
        location = "Выгрузка всех товаров без категории (export_all_prod_for_1c)"
        info = f"ошибка при выгрузке товаров: {e}{tr}"
        e = error_alert(error, location, info)