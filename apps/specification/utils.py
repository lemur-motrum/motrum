import copy
import datetime
from enum import auto
import itertools
import os
from re import T
from apps.core.models import BaseInfo
from apps.core.utils import check_spesc_directory_exist, transform_date
from PIL import Image
import io
import pathlib
from reportlab.lib.units import mm, cm


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
from django.db.models import Prefetch, OuterRef

from apps.logs.utils import error_alert
from project.settings import IS_TESTING, MEDIA_ROOT, MEDIA_URL


# Custom Canvas class for automatically adding page-numbers
class MyCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def draw_page_number(self, page_count):
        # Modify the content and styles according to the requirement
        page = "{curr_page} из {total_pages}".format(
            curr_page=self._pageNumber, total_pages=page_count
        )
        # self.registerFont(TTFont("Roboto", "Roboto-Regular.ttf", "UTF-8"))
        self.setFont("Roboto", 10)

        self.drawRightString(13 * mm, 13 * mm, page)

    def save(self):
        # Modify the save() function to add page-number before saving every page
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_page_number(page_count)
            canvas.Canvas.showPage(self)

        canvas.Canvas.save(self)


def crete_pdf_specification(specification, requisites, account_requisites, request,motrum_requisites,date_delivery_all,type_delivery,post_update,specification_name):
    from apps.product.models import Product, ProductCart, Stock
    from apps.specification.models import ProductSpecification, Specification
    from reportlab.lib.fonts import addMapping
    from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.lib.styles import ParagraphStyle, ListStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.platypus import ListFlowable, ListItem
    try:
        directory = check_spesc_directory_exist(
            "specification",
        )
        specifications = Specification.objects.get(id=specification)
        product_specification = ProductSpecification.objects.filter(
            specification=specification
        ).order_by("id")
        
        
        motrum_info = motrum_requisites.requisites
        motrum_info_req = motrum_requisites
        

        if post_update:
            date_title = specifications.date_create_pdf.strftime("%d/%m/%Y")
            date_data = specifications.date_create_pdf.isoformat()
            date = transform_date(date_data)
        else:
            date_title = datetime.datetime.today().strftime("%d/%m/%Y")
            date_data = datetime.date.today().isoformat()
            date = transform_date(date_data)

        name_specification = f"specification_{specification_name}.pdf"
        fileName = os.path.join(directory, name_specification)
        story = []

        pdfmetrics.registerFont(TTFont("Roboto", "Roboto-Regular.ttf", "UTF-8"))
        pdfmetrics.registerFont(TTFont("Roboto-Bold", "Roboto-Bold.ttf", "UTF-8"))

        addMapping("Roboto", 0, 0, "Roboto")  # normal
        addMapping("Roboto-Bold", 1, 0, "Roboto-Bold")  # bold

        doc = SimpleDocTemplate(
            fileName,
            pagesize=A4,
            rightMargin=10,
            leftMargin=10,
            topMargin=10,
            bottomMargin=50,
            title="Спецификация",
        )

        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(name="Roboto", fontName="Roboto", fontSize=10))
        styles.add(ParagraphStyle(name="Roboto-8", fontName="Roboto", fontSize=8))
        styles.add(ParagraphStyle(name="Roboto-Bold", fontName="Roboto-Bold", fontSize=10))
        styles.add(
            ParagraphStyle(
                name="Roboto-Bold-left",
                fontName="Roboto-Bold",
                fontSize=10,
                alignment=TA_RIGHT,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Roboto-Bold-Center",
                fontName="Roboto-Bold",
                fontSize=10,
                alignment=TA_CENTER,
            )
        )

        bold_style = styles["Roboto-Bold"]
        normal_style = styles["Roboto"]
        bold_left_style = styles["Roboto-Bold-left"]
        bold_style_center = styles["Roboto-Bold-Center"]
        normal_style_8 = styles["Roboto-8"]

        doc_title = copy.copy(styles["Heading1"])
        doc_title.fontName = "Roboto-Bold"
        doc_title.fontSize = 10
        
        if requisites.contract:
            to_contract = requisites.contract
        else:
            to_contract = None   
        if requisites:
            to_address = requisites.legal_entity
        else:
            to_address = ""

        story.append(
            Paragraph(
                f"<b>Спецификация №{specification_name} от {date_title}г.</b><br></br><br></br>", bold_left_style
            )
        )
        if to_contract:
            story.append(Paragraph(f"К договору № {to_contract}", normal_style))
            
        story.append(Paragraph(f"На поставку продукции в адрес {to_address}", normal_style))
        story.append(Paragraph(f'от {motrum_info.short_name_legal_entity} <br></br><br></br>', normal_style))

        data = [
            (
                Paragraph("№ п/п", bold_style_center),
                Paragraph("Номенклатура", bold_style_center),
                Paragraph("Ед. изм.", bold_style_center),
                Paragraph("Кол-во", bold_style_center),
                Paragraph("Цена", bold_style_center),
                Paragraph("Сумма", bold_style_center),
            )
        ]
        # count_total = 0
        i = 0
        date_ship = datetime.date.today()

        product_cart = ProductCart.objects.filter(cart=specifications.cart, product=None)
        product_ = ProductCart.objects.filter(cart=specifications.cart, product=None)
        for product in product_specification:
            i += 1
            try:
                product_stock_item = Stock.objects.get(prod=product.product)
                product_stock = product_stock_item.lot.name_shorts
            except Stock.DoesNotExist:
                product_stock = "шт"
            date_delivery = product.date_delivery
            if date_delivery and date_delivery > date_ship:
                date_ship = date_delivery
            if product.product:
                # if product.product.in_view_website:
                    if IS_TESTING:
                        link = product.product.get_url_document_test()
                    else:
                        link = product.product.get_url_document()

                    url_absolute = request.build_absolute_uri("/").strip("/")
                    link = f"{url_absolute}/{link}"
                    product_name_str = str(product.product.name)
                    if product.product.in_view_website:
                        product_name = (
                            Paragraph(
                                f'<a href="{link}" color="blue">{product_name_str}</a>',
                                bold_style_center,
                            ),
                        )
                    else:
                         product_name = (
                            Paragraph(
                                f'{product_name_str}',
                                bold_style_center,
                            ))    
                # else:    
                #     product_name_str = str(product.product.name)
                    
                #     product_name = (Paragraph(f"{product_name_str}", bold_style_center),)
            else:
                product_name = product.product_new
                product_name = (Paragraph(f"{product_name}", bold_style_center),)

            product_price = product.price_one
            product_price = "{0:,.2f}".format(product_price).replace(",", " ")
            product_price_all = product.price_all

            product_price_all = "{0:,.2f}".format(product_price_all, ".2f").replace(
                ",", " "
            )

            product_quantity = product.quantity
            data.append(
                (
                    i,
                    product_name,
                    # Paragraph(product_name, normal_style),
                    product_stock,
                    product_quantity,
                    product_price,
                    product_price_all,
                )
            )

        table = Table(data, colWidths=[2 * cm, 7 * cm, 2 * cm, 2 * cm, 3 * cm, 3 * cm],repeatRows=1,)
        table.setStyle(
            TableStyle(
                [
                    ("FONT", (0, 0), (-1, -1), "Roboto", 10),
                    ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ]
            )
        )
        story.append(table)

        total_amount_nds = float(specifications.total_amount) * 20 / (20 + 100)
        total_amount_nds = round(total_amount_nds, 2)

        total_amount = "{0:,.2f}".format(specifications.total_amount).replace(",", " ")
        total_amount_nds = "{0:,.2f}".format(total_amount_nds).replace(",", " ")

        final_price_no_nds_table = [
            (
                None,
                None,
                None,
                Paragraph("<br></br>Итого:", bold_left_style),
                Paragraph(f"{total_amount}  руб.", bold_left_style),
            )
        ]
        table = Table(
            final_price_no_nds_table,
        )
        story.append(table)

        final_total_amount_no_nds = [
            (
                None,
                None,
                None,
                Paragraph("Сумма НДС:", bold_left_style),
                Paragraph(f"{total_amount_nds}  руб.", bold_left_style),
            )
        ]
        table = Table(
            final_total_amount_no_nds,
        )
        story.append(table)
        final_final_price_total = [
            (
                None,
                None,
                None,
                Paragraph("Всего к оплате:", bold_left_style),
                Paragraph(f"{total_amount}  руб.<br></br>", bold_left_style),
            )
        ]

        table = Table(
            final_final_price_total,
        )
        story.append(table)
        date_ship = transform_date(str(date_ship))
        
        i_dop_info = 1
        if date_delivery_all:
        
            story.append(Paragraph(f"{i_dop_info}. Срок поставки: {date_delivery_all}", normal_style))
            i_dop_info += 1
            
        if requisites.prepay_persent:
            if requisites.prepay_persent == 100:
                story.append(
                    Paragraph(
                        f"<br></br>{i_dop_info}. Способ оплаты:100% предоплата.", normal_style
                    )
                )
            else:
                story.append(
                    Paragraph(
                        f"<br></br>{i_dop_info}. {requisites.prepay_persent}% предоплата, {requisites.postpay_persent}% в течение 5 дней с момента отгрузки со склада Поставщика.", normal_style
                    )
                ) 
            i_dop_info += 1  
        
        if type_delivery:
            if type_delivery == "pickup":
                story.append(
                        Paragraph(
                            f"<br></br>{i_dop_info}. Доставка: самовывоз", normal_style
                        )
                    )
            elif  type_delivery == "paid_delivery":
                story.append(
                        Paragraph(
                            f"<br></br>{i_dop_info}. Доставка с терминала Деловых линий в городе Поставщика до терминала Деловых линий в городе Покупателя за счет Покупателя.", normal_style
                        )
                    )
            else:
                pass
                    
                

        data_address = [
            (
                Paragraph("<br></br><br></br>Поставщик:", bold_style),
                Paragraph("Покупатель:", bold_style),
            )
        ]
        text_motrum_ur = f'{motrum_info.short_name_legal_entity}<br />Юридический адрес: {motrum_info.legal_post_code},{motrum_info.legal_city}, {motrum_info.legal_address}<br></br><br></br>'
        text_motrum_post = f"Почтовый адрес: {motrum_info.postal_post_code},{motrum_info.postal_city}, {motrum_info.postal_address}<br></br><br></br>"
        text_motrum_inn = f'ИНН {motrum_info.inn} КПП {motrum_info.kpp}<br />Р/с {motrum_info_req.account_requisites}<br />{motrum_info_req.bank}<br />БИК {motrum_info_req.bic}<br />К/с {motrum_info_req.kpp}<br></br><br></br>'
        if requisites:
            text_buyer_ur = f"{requisites.legal_entity}<br />Юридический адрес: {requisites.legal_post_code}, г. {requisites.legal_city}, {requisites.legal_address}<br></br><br></br>"
            text_buyer_post = f"Почтовый адрес: {requisites.postal_post_code}, г. {requisites.postal_city}, {requisites.postal_address}<br></br><br></br>"
            text_buyer_inn = f"ИНН {requisites.inn} КПП {requisites.kpp}<br />Р/с {account_requisites.account_requisites}<br />{account_requisites.bank}<br />БИК {account_requisites.bic}<br />К/с {account_requisites.kpp}<br></br><br></br>"
        else:

            text_buyer_ur = f"<br />Юридический адрес: , г. , <br></br><br></br>"
            text_buyer_post = f"Почтовый адрес: , г. , <br></br><br></br>"
            text_buyer_inn = (
                f"ИНН  КПП <br />Р/с <br /><br />БИК <br />К/с <br></br><br></br>"
            )

        data_address.append(
            (
                Paragraph(text_motrum_ur, normal_style),
                Paragraph(text_buyer_ur, normal_style),
            )
        )
        data_address.append(
            (
                Paragraph(text_motrum_post, normal_style),
                Paragraph(text_buyer_post, normal_style),
            )
        )
        data_address.append(
            (
                Paragraph(text_motrum_inn, normal_style),
                Paragraph(text_buyer_inn, normal_style),
            )
        )
        data_address.append(
            (
                Paragraph("Подписи сторон:<br></br><br></br>", normal_style),
                None,
            )
        )
        table_address = Table(data_address)
        # name_image = f"{MEDIA_ROOT}/documents/skript.png"
        name_image = request.build_absolute_uri(motrum_info.signature.url)

        signature_motrum = Paragraph(
            f'<br /><img width="100" height="30" src="{name_image}" valign="middle"/>&nbsp Старостина В. П.<br /><font  size="8"> &nbsp &nbsp &nbsp &nbsp &nbsp  &nbsp &nbsp  &nbsp подпись &nbsp &nbsp &nbsp &nbsp  &nbsp  &nbsp  &nbsp  &nbsp  &nbsp  &nbsp        расшифровка</font>',
            normal_style,
        )

        story.append(table_address)
        text_signature = '<br /><font  size="10">____________________ /________________  /</font><br /> &nbsp &nbsp &nbsp &nbsp &nbsp  &nbsp &nbsp  &nbsp подпись &nbsp &nbsp &nbsp &nbsp  &nbsp  &nbsp  &nbsp  &nbsp  &nbsp  &nbsp        расшифровка'
        data_signature = [
            (
                Paragraph("Поставщик:", bold_style),
                Paragraph("Покупатель:", bold_style),
            )
        ]

        data_signature.append(
            (
                signature_motrum,
                Paragraph(text_signature, normal_style_8),
            )
        )
        

        data_signature.append(
            (
                Paragraph(date, normal_style),
                Paragraph(date, normal_style),
            )
        )

        # name_image_press = f"{MEDIA_ROOT}/documents/press.png"
        name_image_press = request.build_absolute_uri(motrum_info.stamp.url)
        press_motrum = Paragraph(
            f'<br /><br /><br /><br /><br />М.П.<img width="100" height="100" src="{name_image_press}" valign="middle"/>',
            normal_style,
        )
        data_signature.append(
            (
                press_motrum,
                Paragraph("<br /><br /><br /><br /><br />М.П.", normal_style),
            )
        )
        table_signature = Table(data_signature)
        story.append(table_signature)

        pdf = doc
        pdf.build(story, canvasmaker=MyCanvas)
        file_path = "{0}/{1}/{2}".format(
            "documents",
            "specification",
            name_specification,
        )
        
        print("file_path",file_path)
        return file_path
    except Exception as e:

            
        error = "error"
        location = "Сохранение документа спецификации админам окт"
        info = f"Сохранение документа спецификации админам окт ошибка {e}"
        e = error_alert(error, location, info)
        
        return None


# путь до спецификаций пдф
def get_document_path(instance, filename):
    directory = check_spesc_directory_exist(
        "specification",
    )
    name_specification = f"спецификация_{instance.id}.pdf"
    file_last_list = filename.split(".")
    type_file = "." + file_last_list[-1]


# путь до счета пдф
def get_document_bill_path(instance, filename):
    directory = check_spesc_directory_exist(
        "bill",
    )
    name_specification = f"счет_{instance.id}.pdf"
    file_last_list = filename.split(".")
    type_file = "." + file_last_list[-1]
