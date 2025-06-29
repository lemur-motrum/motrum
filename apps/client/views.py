from functools import cache
import random
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Prefetch
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.db.models import Q, F, OrderBy, Case, When, Value
from django.db.models.functions import Round
from django.db.models import Sum
from apps.admin_specification.views import specifications
from apps.client.models import (
    AccountRequisites,
    Client,
    ClientRequisites,
    Order,
    PhoneClient,
    Requisites,
    RequisitesAddress,
    RequisitesOtherKpp,
)
from apps.notifications.models import Notification
from apps.specification.models import ProductSpecification
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import os

from apps.client.utils import (
    convert_xlsx_to_pdf,
    convert_xlsx_to_pdf_simple,
    convert_xlsx_to_pdf_advanced,
    create_xlsx_and_pdf_bill
)


def index(request):
    title = "Клиенты"
    context = {
        # "contracts": contracts,
        # "title": title,
        # "servise": servise,
    }
    return render(request, "client/index_client.html", context)


# СТРАНИЦЫ ЛК


# МОИ ЗАКАЗЫ
@login_required
def my_orders(request):
    print(request)
    # current_user = request.user.id

    # cookie = request.COOKIES.get("client_id")
    # client_id = int(cookie)

    # client = Client.objects.get(pk=current_user)

    context = {
        "meta_title": "Мои заказы | Личный кабинет",
    }

    return render(request, "client/my_orders.html", context)


# МОИ ДОКУМЕНТЫ
@login_required
def my_documents(request):
    current_user = request.user.id
    client = Client.objects.get(pk=current_user)

    # notifications = Notification.objects.filter(
    #     client_id=current_user, is_viewed=False
    # ).exclude(type_notification="STATUS_ORDERING").update(is_viewed=True)

    context = {
        "meta_title": "Мои документы | Личный кабинет",
    }
    return render(request, "client/my_documents.html", context)


# МОИ РЕКВИЗИТЫ
@login_required
def my_details(request):
    # cookie = request.COOKIES.get("client_id")
    # client_id = int(cookie)
    current_user = request.user.id
    client = Client.objects.get(pk=current_user)
    req = (
        ClientRequisites.objects.filter(client=client)
        .values_list("requisitesotherkpp__id", flat=True)
        .order_by("id")
    )

    requisites = RequisitesOtherKpp.objects.filter(id__in=req).prefetch_related(
        Prefetch("accountrequisites_set"),
        Prefetch("requisitesaddress_set"),
    )

    context = {
        "meta_title": "Мои реквизиты | Личный кабинет ",
        "details": requisites,
        "requisites": requisites,
    }
    return render(request, "client/my_details.html", context)


# ПЕРСОНАЛЬНЫЕ ДАННЫЕ
@login_required
def my_contacts(request):
    cookie = request.COOKIES.get("client_id")
    client_id = int(cookie)

    client = Client.objects.get(pk=client_id)
    other_phone_client = PhoneClient.objects.filter(client=client)
    context = {
        "meta_title": "Мои контакты | Личный кабинет",
        "client": client,
        "other_phone_client": other_phone_client,
    }
    return render(request, "client/my_contacts.html", context)


# ЗАКАЗ ОТДЕЛЬНАЯ СТРАНИЦА
@login_required
def order_client_one(request, pk):
    order = Order.objects.get(pk=pk)
    is_final_price = False

    print("order.bill_name", order.bill_name)
    if order.bill_name:
        is_final_price = True
        print(" TRUE")
        product = (
            ProductSpecification.objects.filter(specification=order.specification)
            .select_related(
                "product",
                "product__stock",
                "product__stock__lot",
                "product__price",
            )
            .prefetch_related(
                Prefetch(
                    "product__productproperty_set",
                ),
                Prefetch(
                    "product__productimage_set",
                ),
            )
            .annotate(
                bill_name=F("specification__order__bill_name"),
                sale_price=F("price_one"),
                full_price=Case(
                    When(
                        extra_discount=None,
                        then=("sale_price"),
                    ),
                    When(
                        extra_discount__isnull=False,
                        then=Round(F("sale_price") / (100 - F("extra_discount")) * 100,2),
                             
                    ),   
                ),
                price_all_item=F("price_all"),
                sum_full_price=Round(F("full_price") * F("quantity"),2),
            )
        )

    else:
        print("order.bill_nameNONE")
        product = (
            ProductSpecification.objects.filter(specification=order.specification)
            .select_related(
                "product",
                "product__stock",
                "product__stock__lot",
                "product__price",
            )
            .prefetch_related(
                Prefetch(
                    "product__productproperty_set",
                ),
                Prefetch(
                    "product__productimage_set",
                ),
            )
            .annotate(
                bill_name=F("specification__order__bill_name"),
                sale_price=F("price_one"),
                sale_price_all=Round(F("price_one") * F("quantity"),2),
                full_price=Case(
                    When(
                        extra_discount=None,
                        then=("sale_price"),
                    ),
                    When(
                        extra_discount__isnull=False,
                        then=Round(F("sale_price") / (100 - F("extra_discount")) * 100,2),
                    ),
                ),
                price_all_item=F("price_all"),
                sum_full_price=Round(F("full_price") * F("quantity"),2),
            )
        )

    total_full_price = product.aggregate(
        all_sum_sale_price=Sum("price_all_item"),
        all_sum_full_price=Sum("sum_full_price"),
        all_sum_sale=Round(F("all_sum_sale_price") - F("all_sum_full_price"),2),
    )
    total_full_price["all_sum_sale"] = abs(total_full_price["all_sum_sale"])

    if order.id_bitrix:
        num = order.id_bitrix
    else:
        num = ""

    context = {
        "order": order,
        "product": product,
        "is_final_price": is_final_price,
        "total_full_price": total_full_price,
        "meta_title": f"Заказ {num} | Мотрум - автоматизация производства",
    }

    return render(request, "client/client_order_one.html", context)

# ПЕРСОНАЛЬНЫЕ ДАННЫЕ
@login_required
def user_logout(request):
    
    logout(request)
    response = redirect(reverse("core:index"))
    response.set_cookie("client_id", max_age=-1)
    response.set_cookie("cart", max_age=-1)
    context = {
       
    }
    return response


@csrf_exempt
def convert_xlsx_to_pdf_view(request, xlsx_path):
    """
    View для конвертации XLSX файла в PDF
    """
    try:
        # Получаем полный путь к XLSX файлу
        full_xlsx_path = os.path.join(MEDIA_ROOT, xlsx_path)
        
        if not os.path.exists(full_xlsx_path):
            return HttpResponse("XLSX файл не найден", status=404)
        
        # Определяем метод конвертации из параметров
        method = request.GET.get('method', 'simple')
        
        if method == 'advanced':
            pdf_path = convert_xlsx_to_pdf_advanced(full_xlsx_path)
        elif method == 'full':
            pdf_path = convert_xlsx_to_pdf(full_xlsx_path)
        else:
            pdf_path = convert_xlsx_to_pdf_simple(full_xlsx_path)
        
        # Отправляем PDF файл
        with open(pdf_path, 'rb') as f:
            response = FileResponse(f, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            return response
            
    except Exception as e:
        return HttpResponse(f"Ошибка конвертации: {str(e)}", status=500)


@method_decorator(csrf_exempt, name='dispatch')
class BillConversionView(View):
    """
    View для создания и конвертации счетов
    """
    
    def post(self, request, order_id):
        """
        Создает XLSX счет и конвертирует его в PDF
        """
        try:
            order = get_object_or_404(Order, id=order_id)
            
            # Параметры из запроса
            is_contract = request.POST.get('is_contract', 'false').lower() == 'true'
            post_update = request.POST.get('post_update', 'false').lower() == 'true'
            type_save = request.POST.get('type_save', 'new')
            
            # Создаем XLSX и PDF
            result = create_xlsx_and_pdf_bill(
                specification=order.specification.id,
                request=request,
                is_contract=is_contract,
                order=order,
                type_delivery=order.type_delivery,
                post_update=post_update,
                type_save=type_save,
            )
            
            xlsx_path, pdf_path, bill_name, version, name_bill_to_fullname = result
            
            # Возвращаем информацию о созданных файлах
            response_data = {
                'success': True,
                'xlsx_path': xlsx_path,
                'pdf_path': pdf_path,
                'bill_name': bill_name,
                'version': version,
                'name_bill_to_fullname': name_bill_to_fullname
            }
            
            return HttpResponse(
                f"Успешно созданы файлы:<br>"
                f"XLSX: {xlsx_path}<br>"
                f"PDF: {pdf_path}<br>"
                f"Номер счета: {bill_name}<br>"
                f"Версия: {version}",
                content_type='text/html'
            )
            
        except Exception as e:
            return HttpResponse(f"Ошибка создания счета: {str(e)}", status=500)
    
    def get(self, request, order_id):
        """
        Показывает форму для создания счета
        """
        order = get_object_or_404(Order, id=order_id)
        
        html = f"""
        <html>
        <head>
            <title>Создание счета для заказа {order_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .form-group {{ margin-bottom: 15px; }}
                label {{ display: block; margin-bottom: 5px; }}
                input, select {{ padding: 8px; width: 200px; }}
                button {{ padding: 10px 20px; background: #007cba; color: white; border: none; cursor: pointer; }}
                button:hover {{ background: #005a87; }}
            </style>
        </head>
        <body>
            <h2>Создание счета для заказа {order_id}</h2>
            <form method="post">
                <div class="form-group">
                    <label>Тип счета:</label>
                    <select name="is_contract">
                        <option value="false">Счет-оферта</option>
                        <option value="true">Счет</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Тип сохранения:</label>
                    <select name="type_save">
                        <option value="new">Новый</option>
                        <option value="update">Обновить</option>
                        <option value="hard_update">Принудительное обновление</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" name="post_update" value="true">
                        Обновление даты
                    </label>
                </div>
                <button type="submit">Создать XLSX и PDF</button>
            </form>
        </body>
        </html>
        """
        
        return HttpResponse(html, content_type='text/html')