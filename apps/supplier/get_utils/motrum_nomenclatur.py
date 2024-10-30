import datetime
import os
import re
import zipfile
import csv
from simple_history.utils import update_change_reason

from apps import supplier
from apps.core.models import Currency, Vat
from apps.logs.utils import error_alert

from apps.product.models import Lot
from project.settings import MEDIA_ROOT



def one_c_price():
    new_dir = "{0}/{1}".format(MEDIA_ROOT, "ones")
    path_nomenclature = f"{new_dir}/Справочник номенклатуры Мотрум.csv"
    path_storage_motrum = f"{new_dir}/Остатки Мотрум.csv"
    path_storage_pnm = f"{new_dir}/Остатки ПМН.csv"
    
    fieldnames_nomenclature = [
        "Номенклатура",
        None,
        None,
        "Артикул",
        None,
        "Единица измерения",
        "Изготовитель",
        "Категория",
        "Описание",
        "Страна происхождения",
        "Производитель",
        "В группе",
    ]
    
    with open(path_nomenclature, "r", newline="", encoding="MACCYRILLIC") as csvfile:
        reader_nomenk = csv.DictReader(
            csvfile, delimiter=";", fieldnames=fieldnames_nomenclature
        )

        i = 0
        for row_nomenk in reader_nomenk:
            i += 1
            if i > 9:
                # if row_nomenk["В группе"] not in supplier_name:
                #     supplier_name.append(row_nomenk["В группе"])
                if row_nomenk["Номенклатура"] in name_position:
                    position_on += 1
                    
                    
                else:
                    position_error += 1
                    print(row_nomenk)