import copy
import datetime
from enum import auto
import itertools
import os
from pickle import NONE
from re import T
from apps.client.models import Order
from apps.core.models import BaseInfo
from apps.core.utils import check_spesc_directory_exist, transform_date, rub_words
from PIL import Image
import io
import pathlib
from reportlab.lib.units import mm, cm
import num2words


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

from apps.specification.utils import MyCanvas
from project.settings import MEDIA_ROOT, MEDIA_URL, STATIC_ROOT
from django.db.models import Prefetch, OuterRef


def crete_pdf_bill(specification):
    from apps.product.models import Product, ProductCart, Stock
    from apps.specification.models import ProductSpecification, Specification
    from reportlab.lib.fonts import addMapping
    from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.lib.styles import ParagraphStyle, ListStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.platypus import ListFlowable, ListItem

    directory = check_spesc_directory_exist(
        "bill",
    )
    specifications = Specification.objects.get(id=specification)
    product_specification = ProductSpecification.objects.filter(
        specification=specification
    )
    
    motrum_info = BaseInfo.objects.prefetch_related(Prefetch("baseinfoaccountrequisites_set")).all().first()
    
    motrum_info_req = motrum_info.baseinfoaccountrequisites_set.first()

    date_now = transform_date(datetime.date.today().isoformat())

    name_bill = f"bill_{specification}.pdf"
    last_bill_order = Order.objects.filter().exclude(bill_file = None).order_by("bill_date_start").last()
    print(last_bill_order.bill_file)
    # number_bill = 
    fileName = os.path.join(directory, name_bill)
    story = []

    pdfmetrics.registerFont(TTFont("Roboto", "Roboto-Regular.ttf", "UTF-8"))
    pdfmetrics.registerFont(TTFont("Roboto-Bold", "Roboto-Bold.ttf", "UTF-8"))

    addMapping("Roboto", 0, 0, "Roboto")  # normal
    addMapping("Roboto-Bold", 1, 0, "Roboto-Bold")  # bold

    doc = SimpleDocTemplate(
        fileName,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=40,
        bottomMargin=40,
        title="Счет",
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(name="Roboto", fontName="Roboto", fontSize=7))
    styles.add(ParagraphStyle(name="Roboto-8", fontName="Roboto", fontSize=6))
    styles.add(ParagraphStyle(name="Roboto-Bold", fontName="Roboto-Bold", fontSize=7))
    styles.add(ParagraphStyle(name="Roboto-Title", fontName="Roboto-Bold", fontSize=12))
    styles.add(
        ParagraphStyle(
            name="Roboto-Bold-Center",
            fontName="Roboto-Bold",
            fontSize=7,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Roboto-right",
            fontName="Roboto",
            fontSize=7,
            alignment=TA_RIGHT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Roboto-Center-Gray-6",
            fontName="Roboto",
            fontSize=6,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Roboto-Center-Gray-6-left",
            fontName="Roboto",
            fontSize=6,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Roboto-Center-Gray-6-right",
            fontName="Roboto",
            fontSize=6,
            alignment=TA_RIGHT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Roboto-Bold-left",
            fontName="Roboto-Bold",
            fontSize=7,
            alignment=TA_RIGHT,
        )
    )

    bold_style = styles["Roboto-Bold"]
    normal_style = styles["Roboto"]
    
    normal_style_right = styles["Roboto-right"]
    normal_style_6 = styles["Roboto-Center-Gray-6"]
    normal_style_6_right = styles["Roboto-Center-Gray-6-right"]
    bold_style_center = styles["Roboto-Bold-Center"]
    normal_style_8 = styles["Roboto-8"]
    title_style_14 = styles["Roboto-Title"]
    bold_left_style = styles["Roboto-Bold-left"]

    doc_title = copy.copy(styles["Heading1"])
    doc_title.fontName = "Roboto-Bold"
    doc_title.fontSize = 7

    name_image_logo = f"{MEDIA_ROOT}/documents/logo.png"
    logo_motrum = Paragraph(
        f'<img width="155" height="35"  src="{name_image_logo}" />',
        normal_style,
    )
    story.append(logo_motrum)
    # тут вставки бик корпоратив
    data_bank = [
        (
            Paragraph(
                f"{motrum_info_req.bank}",
                normal_style,
            ),
            Paragraph("БИК", normal_style),
            Paragraph(f"{motrum_info_req.bic}", normal_style),
        ),
        (
            None,
            Paragraph("Сч. №", normal_style),
            Paragraph(f"{motrum_info_req.kpp}", normal_style),
        ),
        (
            Paragraph("Банк получателя", normal_style_8),
            None,
            None,
        ),
        (
            Paragraph(f"ИНН {motrum_info.inn} &nbsp &nbsp &nbsp  KПП {motrum_info.kpp} ", normal_style),
            Paragraph("Сч. №", normal_style),
            Paragraph(f"{motrum_info_req.account_requisites}", normal_style),
        ),
        (
            Paragraph(
                f'{motrum_info.full_name_legal_entity}', normal_style
            ),
            None,
            None,
        ),
        (
            Paragraph("Получатель", normal_style_8),
            None,
            None,
        ),
    ]
    table_bank = Table(
        data_bank,
        colWidths=[
            9 * cm,
            2 * cm,
            7 * cm,
        ],
        rowHeights=0.5 * cm,
        hAlign="LEFT",
    )
    table_bank.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                ("BOX", (0, -3), (-1, -1), 0.25, colors.black),
                ("BOX", (0, -3), (-3, -3), 0.25, colors.black),
                ("BOX", (1, 0), (-1, -1), 0.25, colors.black),
                ("BOX", (2, 0), (-1, -1), 0.25, colors.black),
                # ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                # # ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                # ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                # ("BOX", (0, 0), (-1, -1), 2, colors.black),
                # ("BOX", (0, 0), (-1, 1), 2, colors.black),
                # ("BOX", (-1, 1), (0, 0), 2, colors.red),
                # # ('BOX',(-2,-1),(-1,1),2,colors.red),
                # ("BOX", (-1, 0), (-1, -1), 2, colors.black),
                # # ('LINEABOVE',(0,2),(-1,2),2,colors.black)
                # # ('LINEABOVE',(0,-2),(-1,2),2,colors.black)
            ]
        )
    )
    story.append(table_bank)

    name_image_logo_supplier = f"{MEDIA_ROOT}/documents/supplier.png"
    logo_supplier = Paragraph(
        f'<br></br><br></br><br></br><br></br><br></br><br></br><img width="555" height="63"  src="{name_image_logo_supplier}" /><br></br>',
        normal_style,
    )
    story.append(logo_supplier)

    story.append(
        Paragraph(f"Счет на оплату № 1 от {date_now}<br></br><br></br>", title_style_14)
    )

    data_info = []
    data_info.append(
        (
            Paragraph(
                f'<br></br>Поставщик<br></br><font  size="6">(исполнитель):</font>',
                normal_style,
            ),
            Paragraph(
                f'{motrum_info.full_name_legal_entity}, ИНН {motrum_info.inn}, КПП {motrum_info.kpp}, {motrum_info.legal_post_code}, {motrum_info.legal_city}, {motrum_info.legal_address}, тел.: {motrum_info.tel}<br></br>',
                bold_style,
            ),
        )
    )

    data_info.append(
        (
            Paragraph(
                f'Покупатель<br></br><font  size="6">(заказчик):</font>', normal_style
            ),
            Paragraph(
                f'ООО "ПМН МОТРУМ", ИНН 6312115720, КПП 631901001, 443011, Самарская обл, Самара г, 22 Партсъезда ул, дом 207, офис 3, тел.: (846) 300-41-17',
                bold_style,
            ),
        )
    )
    data_info.append(
        (
            Paragraph(f"Основание:", normal_style),
            Paragraph(f"Счет № 1 от {date_now}", bold_style),
        )
    )

    table_info = Table(data_info, colWidths=[2.5 * cm, 14 * cm], hAlign="LEFT")
    table_info.setStyle(
        TableStyle(
            [
                ("LINEABOVE", (0, 0), (-1, 0), 2, colors.black),
                ("FONT", (0, 0), (-1, -1), "Roboto", 7),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.transparent),
            ]
        )
    )
    story.append(table_info)

    data = [
        (
            Paragraph("№ ", bold_style_center),
            Paragraph("Товар (Услуга)", bold_style_center),
            Paragraph("Код", bold_style_center),
            Paragraph("Кол-во", bold_style_center),
            Paragraph("Ед.", bold_style_center),
            Paragraph("Цена", bold_style_center),
            Paragraph("Сумма", bold_style_center),
            Paragraph("Срок поставки", bold_style_center),
        ),
        (
            Paragraph(f"1", normal_style_6),
            Paragraph(f"2", normal_style_6),
            Paragraph(f"3", normal_style_6),
            Paragraph(f"4", normal_style_6),
            Paragraph(f"5", normal_style_6),
            Paragraph(f"6", normal_style_6),
            Paragraph(f"7", normal_style_6),
            Paragraph(f"8", normal_style_6),
        ),
    ]

    i = 0
    date_ship = datetime.date.today()
    is_none_date_delivery = False
    total_product_quantity = 0
    for product in product_specification:
        i += 1
        try:
            product_stock_item = Stock.objects.get(prod=product.product)
            product_stock = product_stock_item.lot.name_shorts
        except Stock.DoesNotExist:
            product_stock = "шт"

        date_delivery = product.date_delivery
        if date_delivery :
            if date_delivery > date_ship:
                date_ship = date_delivery
        else: 
            is_none_date_delivery = True         
            
            
        if product.product:
            product_name = str(product.product.name)
            # product_name = str(product)
            product_code = product.product.article

        else:
            product_name = product.product_new
            product_code = "000"

        product_price = product.price_one
        product_price = "{0:,.2f}".format(product_price).replace(",", " ")
        product_price_all = product.price_all
        product_price_all = "{0:,.2f}".format(product_price_all).replace(",", " ")
        product_quantity = product.quantity
        product_data = product.date_delivery
        if product_data:
            product_data = str(product_data.strftime('%d.%m.%Y'))
        else:    
            product_data = str("-")
        total_product_quantity += product_quantity
        data.append(
            (
                i,
                Paragraph(product_name, normal_style),
                product_code,
                product_quantity,
                product_stock,
                product_price,
                product_price_all,
                product_data,
            )
        )
    total_amount_str = "{0:,.2f}".format(specifications.total_amount).replace(",", " ")
    if is_none_date_delivery:
        final_date_ship = "-"
    else:
        final_date_ship = str(date_ship.strftime('%d.%m.%Y')) 
    data.append(
        (
            None,
            None,
            None,
            total_product_quantity,
            None,
            None,
            total_amount_str,
            final_date_ship,
        )
    )

    table_product = Table(
        data,
        colWidths=[
            1 * cm,
            6 * cm,
            2.5 * cm,
            2 * cm,
            1 * cm,
            2.5 * cm,
            2.5 * cm,
            2 * cm,
        ],
        repeatRows=2,
    )
    table_product.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), "Roboto", 7),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                # ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.black),
                ("BOX", (0, 0), (-1, -1), 2, colors.black),
                ("BOX", (0, 0), (-1, 1), 2, colors.black),
                ("BOX", (-1, 1), (0, 0), 2, colors.red),
                # ('BOX',(-2,-1),(-1,1),2,colors.red),
                ("BOX", (-1, 0), (-1, -1), 2, colors.black),
                # ('LINEABOVE',(0,2),(-1,2),2,colors.black)
                # ('LINEABOVE',(0,-2),(-1,2),2,colors.black)
            ]
        )
    )
    story.append(table_product)

    total_amount_nds = float(specifications.total_amount) / 100 * 20
    total_amount_no_nds = float(specifications.total_amount) - total_amount_nds
    total_amount_nds = round(total_amount_nds, 2)
    total_amount_no_nds = round(total_amount_no_nds, 2)

    total_amount = "{0:,.2f}".format(specifications.total_amount).replace(",", " ")
    total_amount_no_nds = "{0:,.2f}".format(total_amount_no_nds).replace(",", " ")
    total_amount_nds = "{0:,.2f}".format(total_amount_nds).replace(",", " ")

    final_price_no_nds_table = [
        (
            None,
            None,
            None,
            None,
            Paragraph("<br></br>Итого:", bold_left_style),
            None,
            Paragraph(f"{total_amount_no_nds}", bold_left_style),
            None,
        )
    ]
    table_product = Table(
        final_price_no_nds_table,
    )
    story.append(table_product)

    final_total_amount_no_nds = [
        (
            None,
            None,
            None,
            None,
            Paragraph("Сумма НДС:", bold_left_style),
            None,
            Paragraph(f"{total_amount_nds} ", bold_left_style),
            None,
        )
    ]
    table_product = Table(
        final_total_amount_no_nds,
    )
    story.append(table_product)
    final_final_price_total = [
        (
            None,
            None,
            None,
            None,
            Paragraph("Всего к оплате:", bold_left_style),
            None,
            Paragraph(f"{total_amount}<br></br>", bold_left_style),
            None,
        )
    ]

    table_product = Table(
        final_final_price_total,
    )
    story.append(table_product)
    total_amount_word = num2words.num2words(
        int(specifications.total_amount), lang="ru"
    ).capitalize()
    total_amount_pens = str(specifications.total_amount).split(".")
    total_amount_pens = total_amount_pens[1]
    print(total_amount_pens)
    if len(total_amount_pens) < 2:
        total_amount_pens = f"{total_amount_pens}0"
    rub_word = rub_words(int(specifications.total_amount))

    story.append(
        Paragraph(
            f"Всего наименований {i}, на сумму {total_amount_str} руб.", normal_style
        )
    )
    story.append(
        Paragraph(
            f"{total_amount_word} {rub_word} {total_amount_pens} копеек", bold_style
        )
    )

    story.append(
        Paragraph(
            f"<br></br><br></br>Оплата данного счета означает согласие с условиями поставки товара.",
            normal_style,
        )
    )
    story.append(
        Paragraph(
            f"Уведомление об оплате обязательно, в противном случае не гарантируется наличие товара на складе.",
            normal_style,
        )
    )
    story.append(
        Paragraph(
            f"Товар отпускается по факту прихода денег на р/с Поставщика, самовывозом, при наличии доверенности и паспорта.",
            normal_style,
        )
    )

    name_image = f"{MEDIA_ROOT}/documents/skript.png"
    signature_motrum = Paragraph(
        f'<br /><img width="100" height="30" src="{name_image}" valign="middle"/>',
        normal_style,
    )
    signature_motrum_name = Paragraph(f"Старостина В. П.", normal_style)
    name_image_press = f"{MEDIA_ROOT}/documents/press.png"
    press_motrum = Paragraph(
        f'<br /><br /><br /><br /><br />М.П.<img width="100" height="100" src="{name_image_press}" valign="middle"/>',
        normal_style,
    )

    data_signature = [
        (
            Paragraph("Руководитель:", bold_style),
            signature_motrum,
            signature_motrum_name,
        ),
        (
            Paragraph("Бухгалтер:", bold_style),
            signature_motrum,
            signature_motrum_name,
        ),
        (
            None,
            press_motrum,
            None,
        ),
    ]

    table_signature = Table(
        data_signature, colWidths=[3 * cm, 5 * cm, 7 * cm], hAlign="LEFT"
    )
    table_signature.setStyle(
        TableStyle(
            [
                ("LINEABOVE", (0, 0), (-1, 0), 2, colors.black),
                ("FONT", (0, 0), (-1, -1), "Roboto", 7),
                ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.transparent),
            ]
        )
    )
    story.append(table_signature)

    pdf = doc
    pdf.build(story, canvasmaker=MyCanvas)
    file_path = "{0}/{1}/{2}".format(
        "documents",
        "bill",
        name_bill,
    )

    return file_path
