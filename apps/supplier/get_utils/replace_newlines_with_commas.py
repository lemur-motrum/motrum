import openpyxl
import re

from project.settings import MEDIA_ROOT

def xlsx_props():

    # Открываем исходный файл
    input_path = f'{MEDIA_ROOT}/documents/filter/filter_comma2.xlsx'
    output_path = f'{MEDIA_ROOT}/documents/filter/filter_comma22.xlsx'

    wb = openpyxl.load_workbook(input_path)
    

    

    # Сохраняем в новый файл
    wb.save(output_path)
    print(f'Готово! Файл сохранён как: {output_path}') 