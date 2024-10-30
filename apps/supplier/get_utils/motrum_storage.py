import datetime
import re
import openpyxl as openxl
from openpyxl import load_workbook

from project.settings import MEDIA_ROOT


def get_motrum_storage():
    new_dir = "{0}/{1}".format(MEDIA_ROOT, "ones")
    path_storage_motrum = f"{new_dir}/test_pmn.xlsx"
    path_storage_pnm = f"{new_dir}/test_pmn.xlsx"

    def get_group_rows(sheet):
        # a =  [row[0].row for row in sheet.iter_rows(2) if row[0].alignment.indent == 0.0]
        row_index_groupe = [
            row_index
            for row_index, row_dimension in sheet.row_dimensions.items()
            if row_index > 2 and row_dimension.outline_level == 0
        ]
        print(row_index_groupe)
        return row_index_groupe

    def reed_workbook(input_file):
        workbook = load_workbook(input_file)
        data_sheet = workbook.active
        group_rows = get_group_rows(data_sheet)
        
       
        
        for index in range(data_sheet.min_row, data_sheet.max_row):
            row_level = data_sheet.row_dimensions[index].outline_level + 1
            
            print(row_level)
            

#     #     print(row_levels)
        # for index in range(3, 100):
        #     for index in range(1, 100):
        #         pass
        #     for col in data_sheet[index]:
        #         vavl = col.value
        #         print("Товары", vavl)

    
    reed_workbook(path_storage_motrum)
    # excel_doc = openxl.open(filename=path_storage_pnm, data_only=True)
    # sheetnames = excel_doc.sheetnames  # Получение списка листов книги
    # sheet = excel_doc[sheetnames[0]]

    # # Считываем значения с ячейки A1
    # wb = openxl.load_workbook(filename=path_storage_pnm)
    # sh = wb.worksheets[0]
    # print(wb)
    # vendor = []
    # all = []
    # for index in range(1, 100):

    #     row_level = sh.row_dimensions[index].outline_level + 1
    #     # ferst_level = sh.row_dimensions[index - 1].outline_level + 1
    #     # row_levels = sh.iter_rows(min_col=1, max_col=2, max_row=2):
    #     item_value = sh.cell(row=index, column=2).value
    #     if item_value == None:
    #         pass
    #     else:
    #         pass
    #         # print(row_level, item_value)

    #     # if item_value == None and ferst_level != row_level:
    #     #     item_value_name = sh.cell(row=index-1, column=2).value
    #     #     print(item_value_name)

    #     # for col in sh[index]:
    #     #     vavl = col.value

    #     #     print("ТоЭвары", vavl)
    #     # i += 1

    #     # print(rgwert3erow_levels)
