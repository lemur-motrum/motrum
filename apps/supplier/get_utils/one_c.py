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
    fieldnames_storage_motrum = [
        "Номенклатура",
        "Итого по всем складам Остаток",
        "Итого по всем складам Резерв",
        "Итого по всем складам Свободно",
        "Неликвид Мотрум Остаток",
        "Неликвид Мотрум Резерв",
        "Неликвид Мотрум Свободно",
        "Основной склад Остаток",
        "Основной склад Резерв",
        "Основной склад Свободно",
        "Склад для товара БЕЗ УПАКОВКИОстаток",
        "Склад для товара БЕЗ УПАКОВКИ Резерв",
        "Склад для товара БЕЗ УПАКОВКИ Свободно",
        "Склад продаж Мотрум ОС Остаток",
        "Склад продаж Мотрум ОС Резерв",
        "Склад продаж Мотрум ОС Свободно",
    ]
    supplier_name = []
    name_position = []
    with open(path_storage_motrum, "r", newline="", encoding="cp866") as csvfile:
        reader_storage_motrum = csv.DictReader(
            csvfile, delimiter=";", fieldnames=fieldnames_storage_motrum
        )

        i = 0
        for row_storage_motrum in reader_storage_motrum:
            i += 1
            if i > 6:
                if "Заказ" not in row_storage_motrum["Номенклатура"]:
                    name_position.append(row_storage_motrum["Номенклатура"])
    with open(path_storage_pnm, "r", newline="", encoding="cp866") as csvfile:
        reader_storage_motrum = csv.DictReader(
            csvfile, delimiter=";", fieldnames=fieldnames_storage_motrum
        )

        i = 0
        for row_storage_motrum in reader_storage_motrum:
            i += 1
            if i > 6:
                if "Заказ" not in row_storage_motrum["Номенклатура"]:
                    name_position.append(row_storage_motrum["Номенклатура"])            
    print(name_position)                
    position_on = 0
    position_error = 0
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
                    
    print(position_on)         
    print(position_error)     
    print(len(name_position))  
    52
    318        
