import copy
import datetime
from enum import auto
import itertools
import os
from re import T
from apps.core.utils import check_spesc_directory_exist


import reportlab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet

from project.settings import MEDIA_ROOT, MEDIA_URL


# def specification_date_stop():
#     from apps.specification.models import  Specification
#     specification = Specification.objects.filter(tag_stop=False)
#     for specification_item in specification:
#         now = datetime.datetime.now()
#         date = specification_item.date_stop
#         if now == date:
#             specification_item.tag_stop = True
#             specification_item.save()


def crete_pdf_specification(specification):
    from apps.specification.models import ProductSpecification, Specification
    directory = check_spesc_directory_exist(
        "specification",
    )
   

    specifications = Specification.objects.get(id=specification)
    product_specification = ProductSpecification.objects.filter(
        specification=specification
    )
    result = [(f"Итого{specifications.total_amount} руб")]

    data = [
        (
            "Товар",
            "Цена за единицу",
            "Количество",
            "Цена за все",
        )
    ]

    name_specification = f"specification_{specification}.pdf"
    fileName = os.path.join(directory, name_specification)

    pdfmetrics.registerFont(TTFont("Times", "Roboto-Regular.ttf", "UTF-8"))
    pdfmetrics.registerFont(TTFont("Times-Bold", "Roboto-Regular.ttf", "UTF-8"))
    pdfmetrics.registerFont(TTFont("Times-Italic", "Roboto-Regular.ttf", "UTF-8"))
    pdfmetrics.registerFont(TTFont("Times-BoldItalic", "Roboto-Regular.ttf", "UTF-8"))
    from reportlab.lib.fonts import addMapping

    addMapping("Times", 0, 0, "Times")  # normal
    addMapping("Times", 0, 1, "Times-Italic")  # italic
    addMapping("Times", 1, 0, "Times-Bold")  # bold
    addMapping("Times", 1, 1, "Times-BoldItalic")  # italic and bold

    doc = SimpleDocTemplate(
        fileName,
        pagesize=A4,
        rightMargin=10,
        leftMargin=10,
        topMargin=10,
        bottomMargin=10,
        title="Спецификация",
    )
    story = []
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name="Justify", fontName="Times", fontSize=11))
    styles.add(ParagraphStyle(name="Justify-Bold", fontName="Times-Bold"))
    bold_style = styles["Justify-Bold"]
    normal_style = styles["Justify"]
    doc_title = copy.copy(styles["Heading1"])
    doc_title.fontName = "Times-Bold"
    doc_title.fontSize = 16
    title = f"Спецификация {specification}"
    story.append(Paragraph(title, doc_title))

    result_table_style = TableStyle(
        [
            ("FONT", (0, 0), (-1, -1), "Times-Bold", 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("BACKGROUND", (0, 0), (15, -2), colors.lightgrey),
        ]
    )

    normal_table_style = TableStyle(
        [
            ("FONT", (0, 0), (-1, -1), "Times", 10),
            ("ALIGN", (0, 0), (0, -1), "CENTRE"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]
    )
    count_total = 0
    for product in product_specification:
        product_price = product.price_one
        product_price_all = product.price_all
        product_quantity = product.quantity
        count_total += product.quantity
        data.append(
            (
                Paragraph(str(product), normal_style),
                product_price,
                product_quantity,
                product_price_all,
            )
        )
    data.append(
        (
            None,
            "Итого",
            f"штук {count_total}",
            f"{specifications.total_amount}рублей",
        )
    )
    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), "Times", 10),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )
    story.append(table)

    # story.append(Spacer(1, 10))
    # doc_title.fontSize = 12

    pdf = SimpleDocTemplate(fileName)
    pdf.build(story)
   
    file_path = "{0}/{1}".format(
        "specification",
        name_specification,
    )
    
    return file_path

def get_document_path(instance, filename):
    directory = check_spesc_directory_exist(
        "specification",
    )
    name_specification = f"спецификация_{instance.id}.pdf"
    file_last_list = filename.split(".")
    type_file = "." + file_last_list[-1]