import datetime
import itertools
import os
from re import T
from apps.specification.models import ProductSpecification, Specification
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link, Rectangle

from project.settings import MEDIA_ROOT


def specification_date_stop():
    specification = Specification.objects.filter(tag_stop=False)
    for specification_item in specification:
        now = datetime.datetime.now()
        date = specification_item.date_stop
        if now == date:
            specification_item.tag_stop = True
            specification_item.save()


# def crete_pdf_specification():

#     pdf_writer = PdfWriter()

#     pdf_page = pdf_writer.add_blank_page (612, 792) 
#     p = {"/T11": "/V2", "/T22": "/V4",}
  
#     pdf_writer.update_page_form_field_values(pdf_page, p, None)
#     print(pdf_page)
#     # Сохраняем созданный PDF-файл

#     with open(os.path.join(MEDIA_ROOT,'new_example1.pdf'), "wb") as pdf_file:
#         pdf_writer.write(pdf_file)
def crete_pdf_specification(specification):
    import reportlab
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle, SimpleDocTemplate
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from django.conf import settings
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.styles import getSampleStyleSheet

    
    # pdfmetrics.registerFont(TTFont('Roboto-Regular', os.path.join(MEDIA_ROOT, "fonts/Roboto-Regular.ttf")))
    
    # reportlab.rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/fonts')
    # pdfmetrics.registerFont(TTFont('Roboto-Regular', 'Roboto-Regular.ttf'))
    
    
    
    # w, h = A4
    # c = canvas.Canvas(os.path.join(MEDIA_ROOT, "report.pdf"), pagesize=A4)
    # text = c.beginText(50, h - 50)
    # text.setFont("Times-Roman", 12)
    # text.textLine("Hello world!")
    # text.textLine("From ReportLab and Python!")
    
    # text.textLines("Hello world!\nFrom ReportLab and Python!")
    # c.drawText(text)
    
    product_specification = ProductSpecification.objects.filter(specification=specification)
    
    # def grouper(iterable, n):
    #     args = [iter(iterable)] * n
    #     return itertools.zip_longest(*args)
    
   
    # def export_to_pdf(data):
    #     c = canvas.Canvas(os.path.join(MEDIA_ROOT, "report2.pdf"), pagesize=A4)
       
    #     w, h = A4
    #     max_rows_per_page = 45
    #     # Margin.
    #     x_offset = 50
    #     y_offset = 50
    #     # Space between rows.
    #     padding = 15

    #     xlist = [x + x_offset for x in [0, 200, 250, 300, 350, 400, 480]]
    #     ylist = [h - y_offset - i*padding for i in range(max_rows_per_page + 1)]

    #     for rows in grouper(data, max_rows_per_page):
    #         rows = tuple(filter(bool, rows))
    #         c.grid(xlist, ylist[:len(rows) + 1])
    #         for y, row in zip(ylist[:-1], rows):
    #             for x, cell in zip(xlist, row):
    #                 c.drawString(x + 2, y - padding + 3, str(cell))
    #         c.showPage()

    #     c.save()
    styles = getSampleStyleSheet()
    styles["Normal"].fontName = 'DejaVuSans'
    styleN = styles["Normal"]
    pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(MEDIA_ROOT, "fonts/DejaVuSans.ttf")))
    data = [("TEXT", ParagraphStyle("Цена за единицу", styleN), "Количество", "Цена за все", )]
    
    
    for product in product_specification:
        product_price = product.price_one
        product_price_all = product.price_all
        product_quantity = product.quantity
        data.append(( ParagraphStyle(product, styleN), product_price, product_price_all, product_quantity))
        
    def myTable(data):
        # pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(MEDIA_ROOT, "fonts/DejaVuSans.ttf")))
        fileName = os.path.join(MEDIA_ROOT, "4.pdf")
        doc = SimpleDocTemplate(fileName, pagesize=A4)
        
    
        colwidths = (60, 320, 60, 60)
        t = Table(data, colwidths)
        t.hAlign = 'RIGHT'
        GRID_STYLE = TableStyle(
            [
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.white),

            ]
        )
        
        t.setStyle(GRID_STYLE)
        elements = []
        elements.append(t)

        
        pdf = SimpleDocTemplate(fileName)

        pdf.build(elements)
        # width = 150
        # height = 150
        # # t.wrapOn(c, width, height)
        # # t.drawOn(c, 65, (0 - height) - 240)
        # c.save()
        
    myTable(data)  
    # export_to_pdf(data)
  

  