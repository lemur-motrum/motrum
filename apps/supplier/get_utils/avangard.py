import os
from unicodedata import category
import openpyxl as openxl
from openpyxl import Workbook
from openpyxl import load_workbook

from project.settings import BASE_DIR


def get_avangard_file():

    file_path = os.path.join(BASE_DIR, "tmp/Odot.xlsx")
    excel_doc = openxl.open(filename=file_path, data_only=True)

    sheetnames = excel_doc.sheetnames
    sheet = excel_doc[sheetnames[0]]
    first = 0

    for i in range(sheet.min_row, sheet.max_row):
        if first == 0:
            if sheet[f"A{i}"].value == "Артикул":
                first = i
            else:
                if sheet[f"C{i}"].value is None:
                    category = sheet[f"C{i}"].value
                    
                    
                    
                    


get_avangard_file()
