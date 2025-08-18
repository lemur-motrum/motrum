import copy
import datetime
from enum import auto
import itertools
from locale import setlocale
import os
from pickle import NONE
from re import T
import re
import traceback

from apps.client.models import Order, OrderDocumentBill
from apps.core.models import BaseImage, BaseInfo, TypeDelivery
from apps.core.utils import check_spesc_directory_exist, transform_date, rub_words
from PIL import Image
import io
import pathlib
from reportlab.lib.units import mm, cm, inch
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

from apps.logs.utils import error_alert
from apps.specification.utils import MyCanvas
from project.settings import IS_TESTING, MEDIA_ROOT, MEDIA_URL, STATIC_ROOT
from django.db.models import Prefetch, OuterRef, Case, When, F
from apps.product.models import Product, ProductCart, Stock
from apps.specification.models import ProductSpecification, Specification
from reportlab.lib.fonts import addMapping
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, ListStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, KeepInFrame
from reportlab.platypus import ListFlowable, ListItem
from reportlab.platypus import Frame, PageBreak


def crete_pdf_bill(
    specification,
    request,
    is_contract,
    order,
    # bill_name,
    type_delivery,
    post_update,
    type_save,
):

    try:
        print("crete_pdf_bill")
        print(type_save)
        directory = check_spesc_directory_exist(
            "bill",
        )
        specifications = Specification.objects.get(id=specification)
        if order.manager:
            name_admin = f"{order.manager.last_name} {order.manager.first_name}"
            if order.manager.middle_name:
                name_admin = f"{order.manager.last_name} {order.manager.first_name} {order.manager.middle_name}"
        else:

            if specifications.admin_creator:
                name_admin = f"{specifications.admin_creator.last_name} {specifications.admin_creator.first_name}"
                if specifications.admin_creator.middle_name:
                    name_admin = f"{specifications.admin_creator.last_name} {specifications.admin_creator.first_name} {specifications.admin_creator.middle_name}"
            else:
                name_admin = " "

        product_specification = ProductSpecification.objects.filter(
            specification=specification
        ).order_by(
            Case(
                When(id_cart__isnull=False, then=0),
                default=1
            ),
            F('id_cart__order'),
            'id'
        )
        print(type_delivery)
        # type_delivery = TypeDelivery.objects.get(id=type_delivery)

        order = Order.objects.get(specification=specification)
        motrum_info = order.motrum_requisites.requisites
        motrum_info_req = order.motrum_requisites

        client_info = order.requisites
        client_info_req_kpp = order.account_requisites.requisitesKpp
        client_info_req = order.account_requisites

        date_now = transform_date(datetime.date.today().isoformat())
        date_name_dot = datetime.datetime.today().strftime("%d.%m.%Y")

        # if post_update:
        #     date_now = order.bill_date_start.isoformat()
        #     date_now = transform_date(date_now)
        #     date_name_dot = order.bill_date_start.strftime("%d.%m.%Y")
        # else:
        #     date_now = transform_date(datetime.date.today().isoformat())
        #     date_name_dot = datetime.datetime.today().strftime("%d.%m.%Y")

        if order.requisites.contract or specifications.total_amount > 99999.99:
            type_bill = "Счет"
            bill_name = motrum_info.counter_bill + 1
            motrum_info.counter_bill = bill_name
        else:
            type_bill = "Счет-оферта"
            bill_name = motrum_info.counter_bill + 1
            motrum_info.counter_bill = bill_name
            # bill_name = motrum_info.counter_bill_offer + 1
            # motrum_info.counter_bill_offer = bill_name

        print("type_bill", type_bill)
        print("bill_name", bill_name)
        print("type_save", type_save)
        print("*******************************")
        if type_save == "new":
            name_bill_text = f"{type_bill} № {bill_name}"
            motrum_info.save()
        elif type_save == "update":
            bill_name = order.bill_name
            name_bill_text = f"{type_bill} № {bill_name}"
        elif type_save == "hard_update":
            name_bill_text = f"{type_bill} № {bill_name}"
            motrum_info.save()
        else:
            bill_name = order.bill_name
            name_bill_text = f"{type_bill} № {bill_name}"
        print("name_bill_text", name_bill_text)
        print("*******************************")

        older_doc = OrderDocumentBill.objects.filter(
            order=order,
            bill_name=bill_name,
            bill_file_no_signature="",
            bill_date_start=datetime.datetime.today(),
        )
        if older_doc:
            print(1, older_doc)
            older_doc_ver = older_doc.last()
            print(2, older_doc_ver)
            version = older_doc_ver.version + 1
            print(2, older_doc_ver)
            text_version = f"_{version}"
        else:
            print(2, older_doc)
            version = 1
            text_version = ""
        print(older_doc)
        print(version)
        print(text_version)
        name_bill_to_fullname = f"{name_bill_text} от {date_now}{text_version}"
        name_bill_to_fullname_nosign = (
            f"{name_bill_text} от {date_now} без печати{text_version}"
        )
        name_bill = f"{name_bill_text} от {date_now}{text_version}.pdf"
        name_bill_no_signature = (
            f"{name_bill_text} от {date_now} без печати{text_version}.pdf"
        )
        document_info = BaseImage.objects.filter().first()

        fileName = os.path.join(directory, name_bill)
        fileName_no_sign = os.path.join(directory, name_bill_no_signature)

        story = []
        story_no_sign = []

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
            bottomMargin=50,
            title="Счет",
        )
        doc_2 = SimpleDocTemplate(
            fileName_no_sign,
            pagesize=A4,
            rightMargin=20,
            leftMargin=20,
            topMargin=40,
            bottomMargin=50,
            title="Счет",
        )

        styles = getSampleStyleSheet()

        styles.add(ParagraphStyle(name="Roboto", fontName="Roboto", fontSize=7))
        styles.add(ParagraphStyle(name="Roboto-8", fontName="Roboto", fontSize=6))
        styles.add(
            ParagraphStyle(name="Roboto-Bold", fontName="Roboto-Bold", fontSize=7)
        )
        styles.add(
            ParagraphStyle(name="Roboto-Title", fontName="Roboto-Bold", fontSize=12)
        )
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
                name="Roboto-left",
                fontName="Roboto",
                fontSize=7,
                alignment=TA_LEFT,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Roboto-centre",
                fontName="Roboto",
                fontSize=7,
                alignment=TA_CENTER,
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
        normal_style_centre = styles["Roboto-centre"]

        normal_style_left = styles["Roboto-left"]
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

        # name_image_logo = f"{MEDIA_ROOT}/documents/logo.png"
        name_image_logo = request.build_absolute_uri(document_info.logo.url)
        logo_motrum = Paragraph(
            f'<img width="155" height="35"  src="{name_image_logo}" />',
            normal_style,
        )

        story.append(logo_motrum)
        story_no_sign.append(logo_motrum)
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
                Paragraph(
                    f"ИНН {motrum_info.inn} &nbsp &nbsp &nbsp  KПП {motrum_info.kpp} ",
                    normal_style,
                ),
                Paragraph("Сч. №", normal_style),
                Paragraph(f"{motrum_info_req.account_requisites}", normal_style),
            ),
            (
                Paragraph(f"{motrum_info.full_name_legal_entity}", normal_style),
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
        story_no_sign.append(table_bank)
        # name_image_logo_supplier = f"{MEDIA_ROOT}/documents/supplier.png"
        name_image_logo_supplier = request.build_absolute_uri(document_info.vendors.url)

        logo_supplier = Paragraph(
            f'<br></br><br></br><br></br><br></br><br></br><br></br><img width="555" height="55"  src="{name_image_logo_supplier}" /><br></br>',
            normal_style,
        )
        story.append(logo_supplier)
        story_no_sign.append(logo_supplier)
        if is_contract or specifications.total_amount > 99999.99:
            story.append(
                Paragraph(
                    f"Счет на оплату № {bill_name} от {date_now}<br></br><br></br>",
                    title_style_14,
                )
            )
            story_no_sign.append(
                Paragraph(
                    f"Счет на оплату № {bill_name} от {date_now}<br></br><br></br>",
                    title_style_14,
                )
            )
        else:
            story.append(
                Paragraph(
                    f"Счет-оферта № {bill_name} от {date_now}<br></br><br></br>",
                    title_style_14,
                )
            )
            story_no_sign.append(
                Paragraph(
                    f"Счет-оферта № {bill_name} от {date_now}<br></br><br></br>",
                    title_style_14,
                )
            )

        data_info = []
        data_info.append(
            (
                Paragraph(
                    f'<br></br>Поставщик<br></br><font  size="6">(исполнитель):</font>',
                    normal_style,
                ),
                Paragraph(
                    f"{motrum_info.full_name_legal_entity}, ИНН {motrum_info.inn}, КПП {motrum_info.kpp}, {motrum_info.legal_post_code}, {motrum_info.legal_city}, {motrum_info.legal_address}, тел.: {motrum_info.tel}<br></br>",
                    bold_style,
                ),
            )
        )

        if client_info.type_client == 1 or client_info.type_client == "1":
            # клиент юрлицо
            info_client = f"{client_info.legal_entity}, ИНН {client_info.inn}, КПП {client_info_req_kpp.kpp}, {client_info_req_kpp.legal_post_code}, {client_info_req_kpp.legal_city} {client_info_req_kpp.legal_address}"

        else:
            # клиент ип
            info_client = f"{client_info.legal_entity}, ИНН {client_info.inn}, ОГРНИП {client_info_req_kpp.ogrn}, {client_info_req_kpp.legal_post_code}, {client_info_req_kpp.legal_city} {client_info_req_kpp.legal_address}"

        if client_info_req_kpp.tel and client_info_req_kpp.tel != "":
            info_client = f"{info_client}, тел.: {client_info_req_kpp.tel}"

        data_info.append(
            (
                Paragraph(
                    f'Покупатель<br></br><font  size="6">(заказчик):</font>',
                    normal_style,
                ),
                Paragraph(
                    info_client,
                    bold_style,
                ),
            )
        )

        data_info.append(
            (
                Paragraph(f"Основание:", normal_style),
                Paragraph(f"Счет {bill_name} от {date_name_dot}", bold_style),
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
                    # ("TOPPADDING", (0, 0), (-1, 0), 1, )
                ]
            )
        )
        story.append(table_info)
        story_no_sign.append(table_info)
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
            print(i, product)
            try:
                product_stock_item = Stock.objects.get(prod=product.product)
                product_stock = product_stock_item.lot.name_shorts
            except Stock.DoesNotExist:
                product_stock = "шт"

            if product.product:
                if IS_TESTING:
                    link = product.product.get_url_document_test()
                else:
                    link = product.product.get_url_document()

                url_absolute = request.build_absolute_uri("/").strip("/")
                link = f"{url_absolute}/{link}"
                product_name_str = product.product.name

                if product.product.supplier.slug == "prompower" and product.product.description:
                    product_name_str = product.product.description
                    # if product.product.name not in product.product.description:
                    #     product_name_str = f"{product.product.name} {product_name_str}"

                if product.product.in_view_website:
                    product_name = (
                        f'<a href="{link}" color="blue">{str(product_name_str)}</a>'
                    )
                else:
                    product_name = f"{str(product_name_str)}"

                product_name = (Paragraph(product_name, normal_style_left),)
                product_code = product.product.article_supplier
                product_code = (Paragraph(product_code, normal_style_left),)

            else:
                product_name = product.product_new
                product_name = (Paragraph(product_name, normal_style_left),)
                product_code = product.product_new_article
                product_code = (Paragraph(product_code, normal_style_left),)

            product_price = product.price_one
            product_price = (
                "{0:,.2f}".format(product_price).replace(",", " ").replace(".", ",")
            )
            product_price_all = product.price_all
            product_price_all = (
                "{0:,.2f}".format(product_price_all).replace(",", " ").replace(".", ",")
            )
            product_quantity = product.quantity
            product_data = product.text_delivery

            # if product.date_delivery_bill:
            #     product_data = str(product.date_delivery_bill.strftime("%d.%m.%Y"))
            # else:
            #     product_data = product.text_delivery

            product_data = (Paragraph(f"{product_data}", normal_style_right),)
            # else:
            #     product_data = str("-")
            total_product_quantity += product_quantity
            data.append(
                (
                    Paragraph(f"{str(i)}", normal_style_centre),
                    product_name,
                    product_code,
                    Paragraph(f"{str(product_quantity)}", normal_style_right),
                    # product_quantity,
                    Paragraph(f"{str(product_stock)}.", normal_style_left),
                    # product_stock,
                    Paragraph(f"{product_price}", normal_style_right),
                    # product_price,
                    Paragraph(f"{product_price_all}", normal_style_right),
                    # product_price_all,
                    product_data,
                )
            )
        total_amount_str = (
            "{0:,.2f}".format(specifications.total_amount)
            .replace(",", " ")
            .replace(".", ",")
        )

        data.append(
            (
                None,
                None,
                None,
                Paragraph(f"{str(total_product_quantity)}", normal_style_right),
                # total_product_quantity,
                None,
                None,
                Paragraph(f"{str(total_amount_str)}", normal_style_right),
                # total_amount_str,
                None,
            )
        )

        table_product = Table(
            data,
            colWidths=[
                1 * cm,
                6 * cm,
                3 * cm,
                1.5 * cm,
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
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    # ('LINEABOVE',(0,2),(-1,2),2,colors.black)
                    # ('LINEABOVE',(0,-2),(-1,2),2,colors.black)
                ]
            )
        )
        story.append(table_product)
        story_no_sign.append(table_product)
        
        
        if order.requisites.prepay_persent:
            if order.requisites.prepay_persent  > 0:
                prepay_persent_text = f"{order.requisites.prepay_persent}% предоплата"
        else:
            prepay_persent_text = ""
        
        if order.requisites.postpay_persent:
            if order.requisites.postpay_persent > 0:
                postpay_persent_text = f"{order.requisites.postpay_persent}% {order.requisites.postpay_persent_text}"
        else:
            postpay_persent_text = ""
       
        if order.requisites.postpay_persent_2:
            if order.requisites.postpay_persent_2 > 0:
                postpay_persent_text_2 = f"{order.requisites.postpay_persent_2}% {order.requisites.postpay_persent_text_2}"
        else:
            postpay_persent_text_2 = ""
        
        if order.requisites.postpay_persent_3:
            if order.requisites.postpay_persent_3 > 0:
                postpay_persent_text_3 = f"{order.requisites.postpay_persent_3}% {order.requisites.postpay_persent_text_3}"
        else:
            postpay_persent_text_3 = ""
   
        
        info_payment_text = ""
        parts_payment = []
        if prepay_persent_text:
            parts_payment.append(prepay_persent_text)
        if postpay_persent_text:
            parts_payment.append(postpay_persent_text)
        if postpay_persent_text_2:
            parts_payment.append(postpay_persent_text_2)
        if postpay_persent_text_3:
            parts_payment.append(postpay_persent_text_3)
        if parts_payment:
            info_payment_text = "" + ", ".join(parts_payment)
        
        info_payment = info_payment_text
        
        

        # if order.requisites.prepay_persent:
        #     if order.requisites.prepay_persent == 100:
        #         info_payment = f"100% предоплата."
        #     elif order.requisites.prepay_persent > 0:
        #         info_payment = f"{order.requisites.prepay_persent}% предоплата, {order.requisites.postpay_persent}% в течение 5 дней с момента отгрузки со склада Поставщика."
        #     else:
        #         info_payment = f"{order.requisites.prepay_persent}% предоплата, {order.requisites.postpay_persent}% в течение 5 дней с момента отгрузки со склада Поставщика."

        # else:
        #     info_payment = ""

        total_amount_nds = float(specifications.total_amount) * 20 / (20 + 100)
        total_amount_nds = round(total_amount_nds, 2)

        total_amount = (
            "{0:,.2f}".format(specifications.total_amount)
            .replace(",", " ")
            .replace(".", ",")
        )
        total_amount_nds = (
            "{0:,.2f}".format(total_amount_nds).replace(",", " ").replace(".", ",")
        )
        final_table_all = []
        # final_table_all.append(
        #     (
               
        #         None,
        #         None,
        #         None,
        #         None,
        #         None,
        #         None,
        #         None,
        #     )
        # )
        final_table_all.append(
            (
                Paragraph(info_payment, normal_style),
               
                None,
                None,
                Paragraph("Итого:", bold_left_style),
                None,
                Paragraph(f"{total_amount}", bold_left_style),
                None,
            )
        )

        final_table_all.append(
            (
                
                None,
                None,
                None,
                Paragraph("В том числе  НДС:", bold_left_style),
                None,
                Paragraph(f"{total_amount_nds} ", bold_left_style),
                None,
            )
        )

        final_table_all.append(
            (
                
                None,
                None,
                None,
                Paragraph("Всего к оплате:", bold_left_style),
                None,
                Paragraph(f"{total_amount}<br></br>", bold_left_style),
                None,
            )
        )

        final_table_all_prod = Table(
            final_table_all,
            colWidths=[
                9 * cm,
                # 1 * cm,
                0.5 * cm,
                0 * cm,
                3 * cm,
                2.5 * cm,
                2.5 * cm,
                2 * cm,
            ],
            splitInRow=1,
        )
        final_table_all_prod2 = Table(
            final_table_all,
            colWidths=[
                9 * cm,
                # 1 * cm,
                0.5 * cm,
                0 * cm,
                3 * cm,
                2.5 * cm,
                2.5 * cm,
                2 * cm,
            ],
            splitInRow=1,
        )
        story.append(final_table_all_prod)
        story_no_sign.append(final_table_all_prod2)

        total_amount_word = num2words.num2words(
            int(specifications.total_amount), lang="ru"
        ).capitalize()
        total_amount_pens = str(specifications.total_amount).split(".")
        total_amount_pens = total_amount_pens[1]

        if len(total_amount_pens) < 2:
            total_amount_pens = f"{total_amount_pens}0"
        rub_word = rub_words(int(specifications.total_amount))
        data_text_info = []
        # data_text_info = [
        #     (
        #         Paragraph(
        #             f"Всего наименований {i}, на сумму {total_amount_str} руб.",
        #             normal_style,
        #         ),
        #     ),
        #     (
        #         Paragraph(
        #             f"{total_amount_word} {rub_word} {total_amount_pens} копеек",
        #             bold_style,
        #         ),
        #     ),
        # ]
        data_text_info.append(
            (
                Paragraph(
                    f"Всего наименований {i}, на сумму {total_amount_str} руб.",
                    normal_style,
                ),
            ),
        )
        data_text_info.append(
            (
                Paragraph(
                    f"{total_amount_word} {rub_word} {total_amount_pens} копеек",
                    bold_style,
                ),
            ),
        )

        if is_contract or specifications.total_amount > 99999.99:
            data_text_info.append(
                (
                    Paragraph(
                        f"<br></br><br></br>Оплата данного счета означает согласие с условиями поставки товара.",
                        normal_style,
                    ),
                )
            )
            data_text_info.append(
                (
                    Paragraph(
                        f"Уведомление об оплате обязательно, в противном случае не гарантируется наличие товара на складе.",
                        normal_style,
                    ),
                )
            )

            if type_delivery.company_delivery is None:

                data_text_info.append(
                    (
                        Paragraph(
                            f"Товар отпускается по факту прихода денег на р/с Поставщика, самовывозом, при наличии доверенности и паспорта.",
                            normal_style,
                        ),
                    )
                )

            else:

                data_text_info.append(
                    (
                        Paragraph(
                            f"Условия доставки: {type_delivery.text_long}",
                            normal_style,
                        ),
                    )
                )

        else:
            data_text_info.append(
                (
                    Paragraph(
                        f"<br></br><br></br>1. Оплата данного счет-оферты означает полное и безоговорочное согласие (акцепт) с условиями поставки товара по наименованию, ассортименту, количеству и цене. Срок действия счета 3 банковских дня.",
                        normal_style,
                    ),
                )
            )
            data_text_info.append(
                (
                    Paragraph(
                        f"2. Поставщик гарантирует отгрузку товара по ценам и в сроки, указанные в настоящем Счет-оферте, при условии зачисления денежных средств на расчетный счет Поставщика в течение 3 банковских дней с даты выставления счета.<br></br>При невыполнении Покупателем указанных условий оплаты, цена и сроки поставки товара могут измениться.",
                        normal_style,
                    ),
                )
            )
            data_text_info.append(
                (
                    Paragraph(
                        f"3. Товар отгружается после полной оплаты счета-оферты Покупателем.",
                        normal_style,
                    ),
                )
            )
            data_text_info.append(
                (
                    Paragraph(
                        f"5. Обязательства Поставщика по поставке Товара считаются выполненными с момента подписания УПД или товарной накладной представителями Поставщика и Покупателя или организации перевозчика.",
                        normal_style,
                    ),
                )
            )
            data_text_info.append(
                (
                    Paragraph(
                        f"6. Каждая партия поставляемой продукции сопровождается Универсальным передаточным документом (УПД): на бумажном носителе в двух экземплярах (1 экз. Покупателя, 1 экз. Поставщика). После каждой поставки продукции с документами, Покупатель обязан вернуть Поставщику один экземпляр, верно оформленного УПД, не позднее 1 месяца с даты подтверждения получения товара. В случае задержки Покупателем возврата, верно оформленного со стороны Покупателя, оригинала УПД на бумажном носителе на срок более 1 (одного) календарного месяца, Поставщик вправе предъявить Покупателю штрафные санкции в размере 5 000 (Пять тысяч) рублей (НДС не облагается) за каждый факт не предоставления подписанного оригинала УПД.",
                        normal_style,
                    ),
                )
            )

            if type_delivery.company_delivery is None:
                data_text_info.append(
                    (
                        Paragraph(
                            f"7. Доставка товара самовывозом со склада Поставщика",
                            normal_style,
                        ),
                    )
                )
            else:

                data_text_info.append(
                    (
                        Paragraph(
                            f"7.{type_delivery.text_long}",
                            normal_style,
                        ),
                    )
                )

            data_text_info.append(
                (
                    Paragraph(
                        f"8. В случае превышения более чем на 15 дней сроков поставки продукции, указанных в Счёте-оферте, Поставщик по требованию Покупателя обязан уплатить неустойку в размере 0,1 % от стоимости не поставленной в срок продукции за каждый день просрочки, но не более 5% от стоимости не поставленной в срок продукции.",
                        normal_style,
                    ),
                )
            )
            data_text_info.append(
                (
                    Paragraph(
                        f"9. Претензии по п. 8 должны быть заявлены Сторонами в письменной форме в течение 5 дней с момента наступления, указанных в них событий. В случае не выставления претензии в указанный срок, это трактуется как освобождение Сторон от уплаты неустойки.",
                        normal_style,
                    ),
                )
            )
            data_text_info.append(
                (
                    Paragraph(
                        f"10. Срок гарантии на поставляемую продукцию составляет не менее одного года с момента отгрузки.",
                        normal_style,
                    ),
                )
            )
            data_text_info.append(
                (
                    Paragraph(
                        f"11. Правила гарантийного обслуживания оговариваются в гарантийных талонах на поставляемую продукцию.",
                        normal_style,
                    ),
                )
            )
            data_text_info.append(
                (
                    Paragraph(
                        f"12.  Стороны принимают необходимые меры к тому, чтобы спорные вопросы и разногласия, возникающие при исполнении и расторжении настоящего договора, были урегулированы путем переговоров. В случае если стороны не достигнут соглашения по спорным вопросам путем переговоров, то спор передается заинтересованной стороной в арбитражный суд.",
                        normal_style,
                    ),
                )
            )

        table_data_text_info = Table(data_text_info, splitInRow=1, hAlign="LEFT")
        table_data_text_info2 = Table(data_text_info, splitInRow=1, hAlign="LEFT")

        table_data_text_info.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 2, colors.transparent),
                    ("FONT", (0, 0), (-1, -1), "Roboto", 7),
                    # ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.transparent),
                ]
            )
        )
        table_data_text_info2.setStyle(
            TableStyle(
                [
                    ("LINEABOVE", (0, 0), (-1, 0), 2, colors.transparent),
                    ("FONT", (0, 0), (-1, -1), "Roboto", 7),
                    # ("ALIGN", (0, 0), (0, -1), "LEFT"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.transparent),
                ]
            )
        )

        print(table_data_text_info)
        # story_no_sign = story.copy()
        story.append(table_data_text_info)
        story_no_sign.append(table_data_text_info2)

        name_image = request.build_absolute_uri(motrum_info.signature.url)
        signature_motrum = Paragraph(
            f'<br /><img width="100" height="30" src="{name_image}" valign="middle"/>',
            normal_style,
        )
        signature_motrum_name = Paragraph(f"Старостина В. П.", normal_style)

        name_image_press = request.build_absolute_uri(motrum_info.stamp.url)

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
            (
                None,
                None,
                Paragraph(
                    f"<br></br><br></br><br></br>{name_admin}", normal_style_right
                ),
            ),
        ]

        table_signature = Table(
            data_signature, colWidths=[3 * cm, 5 * cm, 7 * cm, 7 * cm], hAlign="LEFT"
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

        # Получаем высоту таблицы
        available_width = doc.width - doc.topMargin - doc.rightMargin
        available_height = doc.height - doc.bottomMargin - doc.topMargin
        table_height = table_signature.wrap(available_width, available_height)[1]

        # Считаем общую кумулятивную высоту всех элементов в story
        cumulative_height_of_story = 0
        for element in story:
            if hasattr(element, "wrap"):
                # Предполагается, что doc.height здесь - это максимальная высота,
                # которую элемент МОГ БЫ занять. wrap вернет реальную высоту элемента.
                _w, h = element.wrap(available_width, available_height)
                cumulative_height_of_story += h

        # Теперь вычисляем, какая часть последней страницы занята этим cumulative_height_of_story
        if cumulative_height_of_story == 0:
            height_used_on_final_page_of_story = 0
        else:
            # Если кумулятивная высота точно равна N страницам, то последняя страница полная.
            if (
                cumulative_height_of_story % available_height == 0
                and cumulative_height_of_story > 0
            ):
                height_used_on_final_page_of_story = available_height
            else:
                # Иначе это остаток на последней странице.
                height_used_on_final_page_of_story = (
                    cumulative_height_of_story % available_height
                )

        # total_height теперь представляет высоту, использованную на ПОСЛЕДНЕЙ странице,
        # где заканчивается текущий 'story'.
        total_height = height_used_on_final_page_of_story

        # Оставшееся место = высота страницы - использованная высота на этой последней странице
        remaining_height = available_height - total_height

        table_height_3 = table_height / 3
        table_height_23 = table_height_3 * 2
        print("remaining_height", remaining_height)
        print("table_height_23", table_height_23)
        # Если таблица занимает меньше половины оставшегося места
        if table_height_23 > remaining_height:
            print("66666666666666666666666666666666666666666666666666")
            signature_motrum = Paragraph(
                f'<br /><img width="95" height="25" src="{name_image}" valign="middle"/>',
                normal_style,
            )
            press_motrum = Paragraph(
                f'<br /><br /><br /><br />М.П.<img width="90" height="90" src="{name_image_press}" valign="middle"/>',
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
                    Paragraph(f"{name_admin}", normal_style_right),
                ),
            ]

            table_signature = Table(
                data_signature,
                colWidths=[3 * cm, 5 * cm, 7 * cm, 7 * cm],
                hAlign="LEFT",
            )
            # Уменьшаем отступы в таблице
            table_signature.setStyle(
                TableStyle(
                    [
                        ("LINEABOVE", (0, 0), (-1, 0), 2, colors.black),
                        ("FONT", (0, 0), (-1, -1), "Roboto", 7),
                        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.transparent),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),  # Убираем верхний отступ
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),  # Убираем нижний отступ
                    ]
                )
            )

            # Уменьшаем отступы в параграфах
            for row in data_signature:
                for cell in row:
                    if isinstance(cell, Paragraph):
                        cell.style.spaceBefore = 0
                        cell.style.spaceAfter = 0

        story.append(table_signature)

        # Создаем PDF
        pdf = doc
        pdf = pdf.build(story, canvasmaker=MyCanvas)

        file_path = "{0}/{1}/{2}".format(
            "documents",
            "bill",
            name_bill,
        )
        print(file_path)

        print(333333333333333333)

        data_signature = [
            (
                Paragraph(f"<br /><br />Руководитель:", bold_style),
                Paragraph(f"________________________________", normal_style_centre),
                Paragraph(
                    f"__________________________________________________________",
                    normal_style_centre,
                ),
            ),
            (
                None,
                Paragraph(f"   подпись           ", normal_style_centre),
                Paragraph(f"       расшифровка подписи      ", normal_style_centre),
            ),
            (
                Paragraph("Бухгалтер:", bold_style),
                Paragraph(f"________________________________", normal_style_centre),
                Paragraph(
                    f"__________________________________________________________",
                    normal_style_centre,
                ),
            ),
            (
                None,
                Paragraph(f"   подпись           ", normal_style_centre),
                Paragraph(f"       расшифровка подписи      ", normal_style_centre),
            ),
            (
                Paragraph(f"<br /><br /><br /><br />МП.", normal_style_right),
                None,
                None,
            ),
            (
                None,
                None,
                Paragraph(
                    f"<br></br><br></br><br></br>{name_admin}", normal_style_right
                ),
            ),
        ]

        table_signature = Table(
            data_signature, colWidths=[3 * cm, 5 * cm, 7 * cm, 7 * cm], hAlign="LEFT"
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

        # Получаем высоту таблицы
        available_width = doc_2.width - doc_2.topMargin - doc_2.rightMargin
        available_height = doc_2.height - doc_2.bottomMargin - doc_2.topMargin
        table_height = table_signature.wrap(available_width, available_height)[1]

        # Считаем общую кумулятивную высоту всех элементов в story
        cumulative_height_of_story = 0
        for element in story_no_sign:
            if hasattr(element, "wrap"):
                # Предполагается, что doc.height здесь - это максимальная высота,
                # которую элемент МОГ БЫ занять. wrap вернет реальную высоту элемента.
                _w, h = element.wrap(available_width, available_height)
                cumulative_height_of_story += h

        # Теперь вычисляем, какая часть последней страницы занята этим cumulative_height_of_story
        if cumulative_height_of_story == 0:
            height_used_on_final_page_of_story = 0
        else:
            # Если кумулятивная высота точно равна N страницам, то последняя страница полная.
            if (
                cumulative_height_of_story % available_height == 0
                and cumulative_height_of_story > 0
            ):
                height_used_on_final_page_of_story = available_height
            else:
                # Иначе это остаток на последней странице.
                height_used_on_final_page_of_story = (
                    cumulative_height_of_story % available_height
                )

        # total_height теперь представляет высоту, использованную на ПОСЛЕДНЕЙ странице,
        # где заканчивается текущий 'story'.
        total_height = height_used_on_final_page_of_story

        # Оставшееся место = высота страницы - использованная высота на этой последней странице
        remaining_height = available_height - total_height

        table_height_3 = table_height / 3
        table_height_23 = table_height_3 * 2
        print("remaining_height", remaining_height)
        print("table_height_23", table_height_23)
        # Если таблица занимает меньше половины оставшегося места
        if table_height_23 > remaining_height:
            print("66666666666666666666666666666666666666666666666666")
            signature_motrum = Paragraph(
                f'<br /><img width="95" height="25" src="{name_image}" valign="middle"/>',
                normal_style,
            )
            press_motrum = Paragraph(
                f'<br /><br /><br /><br />М.П.<img width="90" height="90" src="{name_image_press}" valign="middle"/>',
                normal_style,
            )

            data_signature = [
            (
                Paragraph(f"<br />Руководитель:", bold_style),
                Paragraph(f"________________________________", normal_style_centre),
                Paragraph(
                    f"__________________________________________________________",
                    normal_style_centre,
                ),
            ),
            (
                None,
                Paragraph(f"   подпись           ", normal_style_centre),
                Paragraph(f"       расшифровка подписи      ", normal_style_centre),
            ),
            (
                Paragraph("Бухгалтер:", bold_style),
                Paragraph(f"________________________________", normal_style_centre),
                Paragraph(
                    f"__________________________________________________________",
                    normal_style_centre,
                ),
            ),
            (
                None,
                Paragraph(f"   подпись           ", normal_style_centre),
                Paragraph(f"       расшифровка подписи      ", normal_style_centre),
            ),
            (
                Paragraph(f"<br /><br />МП.", normal_style_right),
                None,
                Paragraph(
                    f"{name_admin}", normal_style_right
                ),
            ),
            
        ]

            table_signature = Table(
                data_signature,
                colWidths=[3 * cm, 5 * cm, 7 * cm, 7 * cm],
                hAlign="LEFT",
            )
            # Уменьшаем отступы в таблице
            table_signature.setStyle(
                TableStyle(
                    [
                        ("LINEABOVE", (0, 0), (-1, 0), 2, colors.black),
                        ("FONT", (0, 0), (-1, -1), "Roboto", 7),
                        ("ALIGN", (0, 0), (0, -1), "RIGHT"),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.transparent),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),  # Убираем верхний отступ
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),  # Убираем нижний отступ
                    ]
                )
            )

            # Уменьшаем отступы в параграфах
            for row in data_signature:
                for cell in row:
                    if isinstance(cell, Paragraph):
                        cell.style.spaceBefore = 0
                        cell.style.spaceAfter = 0

        story_no_sign.append(table_signature)

        # Создаем PDF
        pdf_no_sign = doc_2
        pdf_no_sign = pdf_no_sign.build(story_no_sign, canvasmaker=MyCanvas)

        file_path_no_sign = "{0}/{1}/{2}".format(
            "documents",
            "bill",
            name_bill_no_signature,
        )

        return (
            file_path,
            bill_name,
            file_path_no_sign,
            version,
            name_bill_to_fullname,
            name_bill_to_fullname_nosign,
        )

    except Exception as e:
        tr = traceback.format_exc()
        error = "error"
        location = "Сохранение пдф счета "
        info = f"Сохранение пдф счета  ошибка {e}{tr}"
        e = error_alert(error, location, info)
