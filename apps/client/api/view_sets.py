import datetime
import math
from operator import itemgetter
import os
import re
from itertools import chain
from xmlrpc.client import boolean
from django.conf import settings
from django.db.models import Prefetch
from django.db import IntegrityError, transaction

# from regex import F
from django.template import loader
from django.template.loader import render_to_string
from rest_framework import routers, serializers, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.contrib.auth import authenticate, login
from django.db.models import Q, F, OrderBy, Count
from django.db.models import Case, When, Value, IntegerField
from apps import specification
from apps.core.models import BaseInfoAccountRequisites
from apps.logs.utils import error_alert
from apps.notifications.models import Notification

from apps.client.api.serializers import (
    AccountRequisitesSerializer,
    AllAccountRequisitesSerializer,
    ClientRequisitesSerializer,
    ClientSerializer,
    DocumentSerializer,
    EmailsCallBackSerializer,
    LkOrderDocumentSerializer,
    LkOrderSerializer,
    OrderOktSerializer,
    OrderSaveCartSerializer,
    OrderSerializer,
    RequisitesSerializer,
)
from django.contrib.sessions.models import Session
from apps.client.models import (
    STATUS_ORDER,
    STATUS_ORDER_INT,
    AccountRequisites,
    Client,
    EmailsCallBack,
    Order,
    Requisites,
)
from apps.core.utils import (
    create_time_stop_specification,
    get_presale_discount,
    loc_mem_cache,
    save_new_product_okt,
    save_specification,
)
from apps.core.utils_web import (
    _get_pin,
    _verify_pin,
    get_product_item_data,
    send_email_message,
    send_email_message_html,
    send_pin,
)
from apps.product.api.serializers import ProductCartSerializer
from apps.product.models import Cart, Lot, Price, Product, ProductCart
from apps.specification.api.serializers import (
    ProductSpecificationSerializer,
    ProductSpecificationToAddBillSerializer,
    SpecificationSerializer,
)
from apps.specification.models import ProductSpecification, Specification
from apps.specification.utils import crete_pdf_specification
from apps.user.models import AdminUser


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    http_method_names = ["get", "post", "put", "update"]

    # РЕГИСТРАЦИЯ ИЛИ АВТОРИЗАЦИЯ
    @action(detail=False, methods=["post"], url_path=r"login")
    def create_or_login_users(self, request, *args, **kwargs):
        data = request.data
        # phone = data["phone"].replace(" ", "")
        phone = re.sub(r"[^0-9+]+", r"", data["phone"])
        pin_user = data["pin"]
        data["is_active"] = True
        data["username"] = phone
        cart_id = request.COOKIES.get("cart")

        # pin = _get_pin(4)
        pin = 1111
        cache.set(phone, pin, 120)
        # первый шаг отправка пин
        if pin_user == "":
            # cache.set(phone, pin, 120)
            # send_pin(pin, phone)
            return Response(pin, status=status.HTTP_200_OK)

        # сравнение пин и логин
        else:
            verify_pin = _verify_pin(phone, int(pin_user))
            # коды совпадают
            if verify_pin:
                serializer = self.serializer_class(data=data, many=False)
                # создание новый юзер
                if serializer.is_valid():
                    client = serializer.save()
                    client.add_manager()

                # старый юзер логин
                else:
                    client = Client.objects.get(username=phone)
                    serializer = ClientSerializer(client, many=False)

                # юзер логин
                if client.is_active:
                    # логин старого пользователя
                    if client.last_login:
                        login(request, client)

                        try:
                            cart = Cart.objects.get(client=client, is_active=False)
                            if cart_id is None:
                                response = Response()
                                response.data = serializer.data["id"]
                                response.status = status.HTTP_200_OK
                                response.set_cookie("cart", cart.id, max_age=2629800)
                                return response
                            else:

                                product_cart_no_user = ProductCart.objects.filter(
                                    cart=cart_id
                                )
                                for products_no_user in product_cart_no_user:
                                    products_no_user.cart = cart
                                    products_no_user.save()

                                product_cart_no_user.delete()
                                response = Response()
                                response.data = serializer.data["id"]
                                response.status = status.HTTP_200_OK
                                response.set_cookie("cart", cart.id, max_age=2629800)
                                return response
                                # return Response(serializer.data, status=status.HTTP_200_OK)

                        except Cart.DoesNotExist:
                            Cart.objects.filter(id=cart_id).update(client=client)
                            return Response(serializer.data, status=status.HTTP_200_OK)
                        # if cart_id:
                        #     Cart.objects.filter(id=cart_id).update(client=client)

                        # if  Cart.objects.get(client=client,is_active=False) :
                        #     response = Response()
                        #     response.data = serializer.data["id"]
                        #     response.status = status.HTTP_200_OK
                        #     response.set_cookie("cart", Cart.id, max_age=2629800)
                        #     return response
                        # else:
                        #     return Response(serializer.data, status=status.HTTP_200_OK)

                        # return Response(serializer.data, status=status.HTTP_200_OK)
                    # логин нового пользоваеля
                    else:

                        login(request, client)
                        if cart_id:
                            Cart.objects.filter(id=cart_id).update(client=client)
                        return Response(serializer.data, status=status.HTTP_201_CREATED)

                else:
                    return Response(serializer.data, status=status.HTTP_403_FORBIDDEN)

            # коды не совпадают
            else:
                return Response(pin, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path=r"get-client-requisites")
    def get_client_requisites(self, request, *args, **kwargs):
        serializer_class = AccountRequisitesSerializer
        data = request.data
        requisites_serch = data["client"]
        queryset = Requisites.objects.filter(
            Q(legal_entity__icontains=requisites_serch)
            | Q(inn__icontains=requisites_serch)
        )
        serializer = AllAccountRequisitesSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClientRequisitesAccountViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientRequisitesSerializer
    http_method_names = ["get", "post", "update"]


class RequisitesViewSet(viewsets.ModelViewSet):
    queryset = Requisites.objects.all()
    serializer_class = RequisitesSerializer
    http_method_names = ["get", "post", "update"]

    def get_serializer(self, *args, **kwargs):
        # add many=True if the data is of type list
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

        return super(RequisitesViewSet, self).get_serializer(*args, **kwargs)

    @action(detail=False, methods=["post"], url_path=r"add")
    def add_all_requisites(self, request, *args, **kwargs):
        data = request.data
        i = -1
        valid_all = True
        serializer_data_new = []
        for data_item in data:
            i += 1
            requisites = data_item.get("requisites")

            account_requisites_data = data_item.get("account_requisites")

            serializer = self.serializer_class(data=requisites, many=False)

            if serializer.is_valid():

                requisites_item = serializer.save()
                serializer_data_new.append(serializer.data)

                for account_requisites_item in account_requisites_data:
                    account_requisites_item["requisites"] = requisites_item.id

                serializer_class_new = AccountRequisitesSerializer
                serializer = serializer_class_new(
                    data=account_requisites_data, many=True
                )
                if serializer.is_valid():
                    account_requisites_item = serializer.save()
                    serializer_data_new[i]["account_requisites"] = serializer.data

                else:
                    valid_all = False
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                valid_all = False
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if valid_all:
            return Response(serializer_data_new, status=status.HTTP_200_OK)

    @action(detail=True, methods=["update"], url_path=r"update")
    def update_requisites(self, request, pk=None, *args, **kwargs):

        queryset = Requisites.objects.get(pk=pk)
        data = request.data
        serializer_data_new = []
        valid_all = True

        for data_item in data:
            requisites = data_item.get("requisites")
            account_requisites_data = data_item.get("account_requisites")

            serializer = self.serializer_class(queryset, data=requisites, partial=True)
            if serializer.is_valid():
                serializer.save()
                serializer_data_new.append(serializer.data)
                account_requisites = []

                for account_requisites_data_item in account_requisites_data:

                    serializer_class_new = AccountRequisitesSerializer
                    queryset = AccountRequisites.objects.get(
                        pk=account_requisites_data_item["id"]
                    )
                    serializer = serializer_class_new(
                        queryset,
                        data=account_requisites_data_item,
                        partial=True,
                    )
                    if serializer.is_valid():
                        account_requisites_item = serializer.save()
                        account_requisites.append(serializer.data)

                    else:
                        valid_all = False
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )
            else:
                valid_all = False
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if valid_all:
            serializer_data_new[0]["account_requisites"] = account_requisites
            return Response(serializer_data_new, status=status.HTTP_200_OK)


class AccountRequisitesViewSet(viewsets.ModelViewSet):
    queryset = AccountRequisites.objects.all()
    serializer_class = AccountRequisitesSerializer

    http_method_names = ["get", "post", "put", "update"]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    http_method_names = ["get", "post", "put", "update"]

    # сохранение заказа с сайта
    @action(detail=False, methods=["post"], url_path=r"add_order")
    def add_order(self, request, *args, **kwargs):
        data = request.data
        cart = Cart.objects.get(id=data["cart"])
        client = cart.client
        extra_discount = client.percent
        products_cart = ProductCart.objects.filter(cart_id=cart)
        all_info_requisites = False
        all_info_product = True
        requisites_id = None
        account_requisites_id = None

        if "requisites" in data:
            all_info_requisites = True
            requisites = Requisites.objects.get(id=data["requisites"])
            requisites_id = requisites.id
            account_requisites = AccountRequisites.objects.get(
                requisites=requisites, account_requisites=data["account_requisites"]
            )
            account_requisites_id = account_requisites.id

        for product_cart in products_cart:
            if product_cart.product.price.rub_price_supplier == 0:
                all_info_product = False

        # сохранение спецификации для заказа с реквизитами
        if all_info_requisites and all_info_product:
            # сохранение спецификации
            serializer_class_specification = SpecificationSerializer
            data_stop = create_time_stop_specification()
            data_specification = {
                "cart": cart.id,
                "admin_creator": None,
                "id_bitrix": None,
                "date_stop": data_stop,
            }

            serializer = serializer_class_specification(
                data=data_specification, partial=True
            )
            if serializer.is_valid():
                # serializer._change_reason = "Клиент с сайта"
                serializer.skip_history_when_saving = True
                specification = serializer.save()

                # сохранение продуктов для спецификации
                total_amount = 0.00
                currency_product = False
                for product_item in products_cart:
                    quantity = product_item.quantity
                    product = Product.objects.get(id=product_item.product.id)
                    item_data = get_product_item_data(
                        specification, product, extra_discount, quantity
                    )

                    serializer_class_specification_product = (
                        ProductSpecificationSerializer
                    )
                    serializer_prod = serializer_class_specification_product(
                        data=item_data, partial=True
                    )
                    if serializer_prod.is_valid():
                        serializer_prod._change_reason = "Клиент с сайта"
                        # serializer_prod.skip_history_when_saving = True
                        specification_product = serializer_prod.save()

                    else:
                        return Response(
                            serializer_prod.errors,
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    total_amount += float(item_data["price_all"])
                # # обновить спецификацию пдф

                specification.total_amount = total_amount
                specification._change_reason = "Клиент с сайта"
                # specification.skip_history_when_saving = True
                specification.save()

                pdf = crete_pdf_specification(
                    specification.id, requisites, account_requisites, request
                )
                specification.file = pdf
                specification._change_reason = "Клиент с сайта"
                data_stop = create_time_stop_specification()
                specification.date_stop = data_stop
                specification.tag_stop = True
                # specification.skip_history_when_saving = True
                specification.save()
                specification = specification.id
                requisites = data["requisites"]
                account_requisites = data["account_requisites"]
                status_order = "PAYMENT"

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # сохранение данные заказа БЕЗ реквизит и продукты под вопросом
        else:
            specification = None
            status_order = "PROCESSING"

        # сохранение ордера
        serializer_class = OrderSerializer
        data_order = {
            "client": client,
            "name": 123131,
            "specification": specification,
            "cart": cart.id,
            "status": status_order,
            "requisites": requisites_id,
            "account_requisites": account_requisites_id,
        }
        serializer = self.serializer_class(data=data_order, many=False)
        if serializer.is_valid():
            order = serializer.save()
            if all_info_requisites and all_info_product:
                Notification.add_notification(order.id, "STATUS_ORDERING")

                Notification.add_notification(order.id, "DOCUMENT_SPECIFICATION")
                order.create_bill()
            else:
                pass

            cart.is_active = True
            cart.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # сохранение спецификации дмин специф
    @action(detail=False, methods=["post"], url_path=r"add-order-admin")
    def add_order_admin(self, request, *args, **kwargs):
        data = request.data
        cart = Cart.objects.get(id=data["id_cart"])
        account_requisites_data = int(data["client_requisites"])
        motrum_requisites_data = int(data["motrum_requisites"])
        id_bitrix = int(data["id_bitrix"])
        type_delivery = data["type_delivery"]
        id_specification = data["id_specification"]
        type_save = data["type_save"]

        post_update = data["post_update"]


        account_requisites = AccountRequisites.objects.get(id=account_requisites_data)
        motrum_requisites = BaseInfoAccountRequisites.objects.get(
            id=motrum_requisites_data
        )
        requisites = account_requisites.requisites

        if requisites.prepay_persent == 100:
            pre_sale = True
        else:
            pre_sale = False

        if requisites.client:
            client = requisites.client
        else:
            client = None

        if type_save == "specification":
            last_spec_name = Specification.objects.filter(number__isnull=False).last()
 
            if last_spec_name:
                last_spec_name = last_spec_name.number
                specification_name = int(last_spec_name) + 1
            else:
                specification_name = 1

        elif type_save == "bill":
            specification_name = None

        if post_update:
            specification_name = Specification.objects.get(id=id_specification)
            specification_name = specification_name.number


        try:
         
            with transaction.atomic():

                specification = save_specification(
                    data,
                    pre_sale,
                    request,
                    motrum_requisites,
                    account_requisites,
                    requisites,
                    id_bitrix,
                    type_delivery,
                    post_update,
                    specification_name,
                )

        except Exception as e:
            print(e)
            #   добавление в козину удаленного товара при сохранении спецификации из апдейта
            if data["id_specification"] != None:
                product_cart_list = ProductCart.objects.filter(cart=cart).values_list(
                    "product__id"
                )

                product_spes_list = ProductSpecification.objects.filter(
                    specification_id=data["id_specification"]
                ).exclude(product_id__in=product_cart_list)

                if product_spes_list:
                    for product_spes_l in product_spes_list:
                        new = ProductCart(
                            cart=cart,
                            product=product_spes_l.product,
                            quantity=product_spes_l.quantity,
                        )
                        new.save()

            error = "error"
            location = "Сохранение спецификации админам окт"
            info = f"Сохранение спецификации админам окт ошибка {e}"
            e = error_alert(error, location, info)

        if specification:
            if post_update:
                data_order = {
                    "comment": data["comment"],
                    "name": 123131,
                }
            else:
                data_order = {
                    "client": client,
                    "name": 123131,
                    "specification": specification.id,
                    "requisites": requisites.id,
                    "account_requisites": account_requisites.id,
                    "status": "PROCESSING",
                    "cart": cart.id,
                    "bill_name": None,
                    "bill_file": None,
                    "bill_date_start": None,
                    "bill_date_stop": None,
                    "bill_sum": None,
                    "comment": data["comment"],
                    "prepay_persent": requisites.prepay_persent,
                    "postpay_persent": requisites.postpay_persent,
                    "motrum_requisites": motrum_requisites.id,
                    "id_bitrix": id_bitrix,
                    "type_delivery": type_delivery,
                }
            
            try:
                order = Order.objects.get(cart_id=cart)
                serializer = self.serializer_class(order, data=data_order, many=False)
                if serializer.is_valid():
                    serializer._change_reason = "Ручное"
                    serializer.save()
                    cart.is_active = True
                    cart.save()
            
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            except Order.DoesNotExist:

                serializer = self.serializer_class(data=data_order, many=False)
                if serializer.is_valid():
                    cart.is_active = True
                    cart.save()
                    serializer.save()

                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:

                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

    # сохранение заказа в корзины без документов для дальнейшего использования
    @action(detail=False, methods=["post"], url_path=r"add-order-no-spec-admin")
    def add_order_no_spec_admin(self, request, *args, **kwargs):
        data = request.data
        cart = Cart.objects.get(id=data["id_cart"])

        if data["id_bitrix"] != None:
            id_bitrix = int(data["id_bitrix"])
        else:
            id_bitrix = None

        if data["client_requisites"] != None:
            account_requisites_data = int(data["client_requisites"])
            account_requisites = AccountRequisites.objects.get(
                id=account_requisites_data
            )
            requisites = account_requisites.requisites
            requisites_id = requisites.id
            account_requisites_id = account_requisites.id
            prepay_persent = requisites.prepay_persent
            postpay_persent = requisites.postpay_persent
            if requisites.client:
                client = requisites.client
            else:
                client = None
        else:
            account_requisites_id = None
            requisites_id = None
            client = None
            prepay_persent = None
            postpay_persent = None

        if data["motrum_requisites"] != None:
            motrum_requisites_id = int(data["motrum_requisites"])
        else:
            motrum_requisites_id = None

        if data["type_delivery"] != None:
            type_delivery = data["type_delivery"]
        else:
            type_delivery = None

        data_order = {
            "client": client,
            "name": 123131,
            "specification": None,
            "requisites": requisites_id,
            "account_requisites": account_requisites_id,
            "status": "",
            "cart": cart.id,
            "bill_name": None,
            "bill_file": None,
            "bill_date_start": None,
            "bill_date_stop": None,
            "bill_sum": None,
            "comment": data["comment"],
            "prepay_persent": prepay_persent,
            "postpay_persent": postpay_persent,
            "motrum_requisites": motrum_requisites_id,
            "id_bitrix": id_bitrix,
            "type_delivery": type_delivery,
        }

        try:
            order = Order.objects.get(cart=cart)
            serializer = self.serializer_class(order, data=data_order, many=False)
            if serializer.is_valid():
                serializer._change_reason = "Ручное"
                order = serializer.save()
                cart.is_active = True
                cart.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            serializer = self.serializer_class(data=data_order, many=False)
            if serializer.is_valid():
                cart.is_active = True
                cart.save()
                order = serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:

                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # создание счета к заказу
    @action(detail=True, methods=["update"], url_path=r"create-bill-admin")
    def create_bill_admin(self, request, pk=None, *args, **kwargs):
        try:
            data_get = request.data
            post_update = data_get["post_update"]
            products = data_get["products"]
            order = Order.objects.get(specification_id=pk)
            
            for obj in products:
                prod = ProductSpecification.objects.filter(id=obj["id"]).update(
                    text_delivery=obj["text_delivery"]
                )

            if post_update:
                bill_name = order.bill_name
            else:
                bill_name = (
                    Order.objects.filter(bill_name__isnull=False)
                    .order_by("bill_name")
                    .last()
                )
                if bill_name:
                    bill_name = int(bill_name.bill_name) + 1
                else:
                    bill_name = 1

            if order.requisites.contract:
                is_req = True
            else:
                is_req = False

            order_pdf = order.create_bill(
                request, is_req, order, bill_name, post_update
            )

            if order_pdf:
                print(444)
                pdf = request.build_absolute_uri(order.bill_file.url)
                data = {"pdf": pdf, "name_bill": order.bill_name}
                print(data)
                # сохранение товара в окт нового
                for obj in products:

                    prod = ProductSpecification.objects.get(id=obj["id"])

                    if prod.product_new_article != None:
     
                        save_new_product_okt(prod)

                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(None, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            error = "error"
            location = "Сохранение счета админам окт"
            info = f"Сохранение счета админам окт ошибка {e}"
            e = error_alert(error, location, info)

            return Response(e, status=status.HTTP_400_BAD_REQUEST)

    # изменение спецификации дмин специф
    @action(detail=True, methods=["update"], url_path=r"update-order-admin")
    def update_order_admin(self, request, pk=None, *args, **kwargs):
        data = request.data
        cart_id = request.COOKIES.get("cart")
        cart = Cart.objects.filter(id=cart_id).update(is_active=False)
        return Response(cart, status=status.HTTP_200_OK)

    # выйти из изменения без сохранения спецификации дмин специф
    @action(detail=False, methods=["update"], url_path=r"exit-order-admin")
    def exit_order_admin(self, request, *args, **kwargs):
        cart_id = request.COOKIES.get("cart")
        cart = Cart.objects.filter(id=cart_id).update(is_active=True)
        return Response(cart, status=status.HTTP_200_OK)

    # получить список товаров для создания счета с датами псотавки
    @action(detail=True, methods=["get"], url_path=r"get-specification-product")
    def get_specification_product(self, request, pk=None, *args, **kwargs):

        product_specification = ProductSpecification.objects.filter(specification=pk)
        if product_specification.exists():
            serializer = ProductSpecificationToAddBillSerializer(
                product_specification, many=True
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

    # страница мои заказов аякс загрузка
    @action(detail=False, url_path="load-ajax-order-list")
    def load_ajax_order_list(self, request):
        from django.db.models.functions import Length

        count = int(request.query_params.get("count"))
        count_last = 5

        serializer_class = LkOrderSerializer
        current_user = request.user.id
        client = Client.objects.get(pk=current_user)

        # сортировки
        sorting = "-notification_count"
        # direction = "ASC"
        if request.query_params.get("sort"):
            sorting = request.query_params.get("sort")
        if request.query_params.get("direction"):
            direction = request.query_params.get("direction")

        if sorting == "date_order":
            if direction == "ASC":
                sorting = F("date_order").asc(nulls_last=True)
            else:
                sorting = F("date_order").desc(nulls_last=True)

        if sorting == "bill_sum":
            if direction == "ASC":
                sorting = F("bill_sum").asc(nulls_last=True)
            else:
                sorting = F("bill_sum").desc(nulls_last=True)

        if sorting == "status":
            if direction == "ASC":
                sorting = Case(
                    When(status="PROCESSING", then=Value(1)),
                    When(status="PAYMENT", then=Value(2)),
                    When(status="IN_MOTRUM", then=Value(3)),
                    When(status="SHIPMENT_AUTO", then=Value(4)),
                    When(status="SHIPMENT_PICKUP", then=Value(5)),
                    When(status="CANCELED", then=Value(6)),
                    When(status="COMPLETED", then=Value(7)),
                    output_field=IntegerField(),
                )
            else:
                sorting = Case(
                    When(status="PROCESSING", then=Value(7)),
                    When(status="PAYMENT", then=Value(6)),
                    When(status="IN_MOTRUM", then=Value(5)),
                    When(status="SHIPMENT_AUTO", then=Value(4)),
                    When(status="SHIPMENT_PICKUP", then=Value(3)),
                    When(status="CANCELED", then=Value(2)),
                    When(status="COMPLETED", then=Value(1)),
                    output_field=IntegerField(),
                )

        # ОСТАТКИ СОРТИРОВКИ ПО НЕСКОЛЬКИМ ПОЛЯЬ ОДНОВРЕМЕННО НЕ УДАЛЯТЬ
        # if request.query_params.get("sortDate"):
        #     date_get = request.query_params.get("sortDate")
        # else:
        #     date_get = "ASC"
        #     # date_get = None

        # if request.query_params.get("sortSum"):
        #     sum_get = request.query_params.get("sortSum")
        # else:
        #     # sum_get = "ASC"
        #     sum_get = None

        # if request.query_params.get("sortStatus"):
        #     status_get = request.query_params.get("sortStatus")
        # else:
        #     status_get = "ASC"
        # status_get = None

        # if date_get:
        #     sort = "date_order"
        #     if date_get == "ASC":
        #         ordering_filter_date = F(sort).asc(nulls_last=True)
        #     else:
        #         ordering_filter_date = F(sort).desc(nulls_last=True)

        # else:
        #     ordering_filter_date = None

        # if sum_get:
        #     sort = "bill_sum"
        #     if sum_get == "ASC":
        #         ordering_filter_summ = F(sort).asc(nulls_last=True)
        #
        #     else:
        #         ordering_filter_summ = F(sort).desc(nulls_last=True)
        # else:
        #     ordering_filter_summ = None

        # if status_get:
        #     sort = "status"
        #     if status_get == "ASC":

        #         custom_order = Case(
        #             When(status="PROCESSING", then=Value(1)),
        #             When(status="PAYMENT", then=Value(2)),
        #             When(status="IN_MOTRUM", then=Value(3)),
        #             When(status="SHIPMENT_AUTO", then=Value(4)),
        #             When(status="SHIPMENT_PICKUP", then=Value(5)),
        #             When(status="CANCELED", then=Value(6)),
        #             When(status="COMPLETED", then=Value(7)),
        #             output_field=IntegerField(),
        #         )

        #     else:
        #         custom_order = Case(
        #             When(status="PROCESSING", then=Value(7)),
        #             When(status="PAYMENT", then=Value(6)),
        #             When(status="IN_MOTRUM", then=Value(5)),
        #             When(status="SHIPMENT_AUTO", then=Value(4)),
        #             When(status="SHIPMENT_PICKUP", then=Value(3)),
        #             When(status="CANCELED", then=Value(2)),
        #             When(status="COMPLETED", then=Value(1)),
        #             output_field=IntegerField(),
        #         )
        # else:
        #     custom_order = None
        # для такой сортировки если нет данных использовать custom_order ordering_filter_summ ordering_filter_date = None

        # ordering = {
        # 'ordering_filter_date': ordering_filter_date,
        # 'ordering_filter_summ': ordering_filter_summ,
        # 'custom_order': custom_order,
        # }
        # ordering = {k:v for k,v in ordering.items() if v is not None}
        # ordering = list(ordering.values())
        # lot = Lot.objects.all()

        orders = (
            Order.objects.filter(client=client)
            .select_related(
                "specification",
                "cart",
                "requisites",
                "account_requisites",
            )
            # .prefetch_related(
            #     Prefetch(
            #         "notification_set",
            #         queryset=Notification.objects.filter(
            #             type_notification="STATUS_ORDERING", is_viewed=False
            #         ),
            #         to_attr="filtered_notification_items",
            #     )
            # )
            .prefetch_related(Prefetch("specification__productspecification_set"))
            .prefetch_related(
                Prefetch("specification__productspecification_set__product")
            )
            # .prefetch_related(
            #     Prefetch('specification__productspecification_set__product__stock'))
            # .prefetch_related(
            #     Prefetch('specification__productspecification_set__product__stock__lot'))
            .annotate(
                notification_count=Count(
                    "notification",
                    filter=Q(
                        notification__is_viewed=False,
                        notification__type_notification="STATUS_ORDERING",
                    ),
                )
            )
            .order_by(sorting, "-id")[count : count + count_last]
        )

        # [count : count + count_last]
        serializer = serializer_class(orders, many=True)
        data = serializer.data
        # прочитать уведомления только выведенные ордеры
        for data_order in data:
            if int(data_order["notification_count"]) > 0:
                Notification.objects.filter(
                    order=data_order["id"],
                    client_id=current_user,
                    type_notification="STATUS_ORDERING",
                    is_viewed=False,
                ).update(is_viewed=True)

        # прочитать уведомления всех ордеров
        # notifications = Notification.objects.filter(
        #     client_id=current_user, type_notification="STATUS_ORDERING", is_viewed=False
        # ).update(is_viewed=True)

        # if sorting == "-id":
        #     data = sorted(data, key=lambda x: len(x["notification_set"]), reverse=True)

        data_response = {
            "data": data,
        }
        return Response(data=data_response, status=status.HTTP_200_OK)

    # страница мои документы аякс загрузка
    @action(detail=False, url_path="load-ajax-document-list")
    def load_ajax_document_list(self, request):
        count = int(request.query_params.get("count"))
        count_last = 10
        serializer_class = LkOrderDocumentSerializer
        current_user = request.user.id
        client = Client.objects.get(pk=current_user)

        # сортировки
        sorting = None
        # sorting_spesif = "specification__date"
        # sorting_bill = "bill_date_start"
        if request.query_params.get("sort"):
            sorting = request.query_params.get("sort")

        if request.query_params.get("direction"):
            sorting_directing = request.query_params.get("direction")

        # заказы сериализировать
        orders = (
            Order.objects.filter(client=client)
            .select_related(
                "specification",
                "cart",
                "requisites",
                "account_requisites",
            )
            .prefetch_related(
                Prefetch(
                    "notification_set",
                    queryset=Notification.objects.filter(is_viewed=False).exclude(
                        type_notification="STATUS_ORDERING"
                    ),
                    to_attr="filtered_notification_items",
                )
            )
        )

        serializer = serializer_class(orders, many=True)

        # формирование отдельных документов из сериализированных заказов
        documents = []
        for order in serializer.data:

            if order["specification"]:

                data_spesif = {
                    "type": 1,
                    "name": "спецификация",
                    "order": order["id"],
                    "status": order["status"],
                    "status_full": order["status_full"],
                    "pdf": order["specification_list"]["file"],
                    "requisites_contract": order["requisites_full"]["contract"],
                    "requisites_legal_entity": order["requisites_full"]["legal_entity"],
                    "date_created": order["specification_list"]["date"],
                    "data_stop": order["specification_list"]["date_stop"],
                    "amount": order["specification_list"]["total_amount"],
                    "notification_set": [],
                    "type_notification": "DOCUMENT_SPECIFICATION",
                }

                for notification_set in order["notification_set"]:
                    if (
                        notification_set["type_notification"]
                        == "DOCUMENT_SPECIFICATION"
                    ):

                        data_spesif["notification_set"].append(notification_set)

                documents.append(data_spesif)

            if order["bill_file"]:
                data_bill = {
                    "type": 2,
                    "name": "счёт",
                    "order": order["id"],
                    "status": order["status"],
                    "status_full": order["status_full"],
                    "pdf": order["bill_file"],
                    "requisites_contract": order["requisites_full"]["contract"],
                    "requisites_legal_entity": order["requisites_full"]["legal_entity"],
                    "date_created": order["bill_date_start"],
                    "data_stop": order["bill_date_stop"],
                    "amount": order["bill_sum"],
                    "notification_set": [],
                    "type_notification": "DOCUMENT_BILL",
                }

                for notification_set in order["notification_set"]:
                    if notification_set["type_notification"] == "DOCUMENT_BILL":
                        data_bill["notification_set"].append(notification_set)

                documents.append(data_bill)

            # if order["bill_file"]:
            #     data_act = {
            #         "type": 3,
            #         "name": "акт",
            #         "order": order["cart"],
            #         "status": order["status"],
            #         "status_full": order["status_full"],
            #         "pdf": order["bill_file"],
            #         "requisites_contract": order["requisites_full"]["contract"],
            #         "requisites_legal_entity": order["requisites_full"]["legal_entity"],
            #         "date_created": order["bill_date_start"],
            #         "data_stop": order["bill_date_stop"],
            #         "amount": order["bill_sum"],
            #         "notification_set" : []
            #     }
            #  for notification_set in order["notification_set"]:
            #         if notification_set['type_notification'] == 'DOCUMENT_ACT':
            #             data_spesif['notification_set'].append(notification_set)

            #     documents.append(data_act)

        # сортировки для документов
        if sorting:
            if sorting == "date":
                documents = sorted(
                    documents,
                    key=lambda x: datetime.datetime.strptime(
                        x["date_created"], "%d.%m.%Y"
                    ),
                    reverse=sorting_directing,
                )
            else:
                documents = sorted(
                    documents, key=itemgetter(sorting), reverse=sorting_directing
                )
        else:
            documents = sorted(
                documents, key=lambda x: len(x["notification_set"]), reverse=True
            )
        # прочитать уведомления только выведенные ордеры
        # for data_order in documents:
        #     if len(data_order["notification_set"]) > 0:
        #         Notification.objects.filter(order=data_order["order"],
        #         client_id=current_user, type_notification=data_order["type_notification"], is_viewed=False
        #     ).update(is_viewed=True)

        notifications = (
            Notification.objects.filter(client_id=current_user, is_viewed=False)
            .exclude(type_notification="STATUS_ORDERING")
            .update(is_viewed=True)
        )

        data_response = {
            "data": documents[count : count + count_last],
            # [count : count + 10]
        }

        return Response(data=data_response, status=status.HTTP_200_OK)

    # страница все спецификации окт аякс загрузка
    @action(detail=False, url_path=r"load-ajax-specification-list")
    def load_ajax_specification_list(self, request, *args, **kwargs):
        count = int(request.query_params.get("count"))
        count_last = 10
        page_get = request.query_params.get("page")
        q_object = Q()
        if request.user.is_superuser:
            superadmin = True
        else:
            superadmin = False

        user_admin = AdminUser.objects.get(user=request.user)
        user_admin_type = user_admin.admin_type
        if user_admin_type == "ALL":
            q_object &= Q(cart__cart_admin_id__isnull=False)
        elif user_admin_type == "BASE":
            q_object &= Q(cart__cart_admin_id=request.user.id)

        sort_specif = request.query_params.get("specification")

        if sort_specif == "+":
            q_object &= Q(specification__isnull=True)
        else:
            q_object &= Q(specification__isnull=False)

        now_date = datetime.datetime.now()
        queryset = (
            Order.objects.select_related(
                "specification", "cart", "client", "requisites", "account_requisites"
            )
            .prefetch_related(
                Prefetch("specification__admin_creator"),
                Prefetch("cart__productcart_set"),
                Prefetch("cart__productcart_set__product"),
                Prefetch("cart__cart_admin"),
                Prefetch("requisites__accountrequisites_set"),
            )
            .filter(q_object)
            .order_by("-id")[count : count + count_last]
        )


        page_count = Order.objects.filter(q_object).count()

        queryset_next = Order.objects.filter(q_object)[
            count + count_last : count + count_last + 1
        ].exists()

        if page_count % 10 == 0:
            count = page_count / 3
        else:
            count = math.trunc(page_count / 10) + 1

        if page_count <= 10:
            small = True
        else:
            small = False

        serializer = OrderOktSerializer(
            queryset, many=True, context={"request": request}
        )
        data_response = {
            "data": serializer.data,
            "superadmin": superadmin,
            "count": math.ceil(page_count / count_last),
            "small": small,
            "page": page_get,
            "next": queryset_next,
        }
        return Response(data=data_response, status=status.HTTP_200_OK)

    # добавление оплаты открыть получить отстаок суммы
    @action(detail=True, methods=["get"], url_path=r"get-payment")
    def get_payment(self, request, pk=None, *args, **kwargs):
        order = Order.objects.get(id=pk)

        sum_pay = float(order.bill_sum) - float(order.bill_sum_paid)
        data = {
            "sum_pay": sum_pay,
        }
        if sum_pay:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

    # сохранение суммы оплаты счета
    @action(detail=True, methods=["post"], url_path=r"save-payment")
    def save_payment(self, request, pk=None, *args, **kwargs):
        order = Order.objects.get(id=pk)
        data = request.data
        bill_sum_paid = data["bill_sum_paid"]
        old_sum = order.bill_sum_paid
        new_sum = old_sum + float(bill_sum_paid)
        order.bill_sum_paid = new_sum
        order._change_reason = "Ручное"
        order.save()
        if order.bill_sum_paid == order.bill_sum:
            is_all_sum = True
        else:
            is_all_sum = False
        data = {"all_bill_sum_paid": new_sum, "is_all_sum": is_all_sum}
        if new_sum:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(None, status=status.HTTP_400_BAD_REQUEST)

    # получение суммы уже оплаченной при открытии модалки внесения оплаты
    @action(detail=True, methods=["get"], url_path=r"view-payment")
    def view_payment(self, request, pk=None, *args, **kwargs):
        order = Order.objects.filter(id=pk)
        # data = request.data
        # bill_sum_paid = data["bill_sum_paid"]
        # order.bill_sum_paid = float(bill_sum_paid)

        sum_prepay = order.bill_sum - (
            order.bill_sum / 100 * order.requisites.postpay_persent
        )
        sum_postpay = order.bill_sum - sum_prepay
        if order.bill_sum_paid >= sum_prepay:
            sum_prepay_fact = order.bill_sum_paid
            sum_postpay_fact = order.bill_sum_paid - sum_prepay_fact
        else:
            sum_prepay_fact = sum_prepay - order.bill_sum_paid
            sum_postpay_fact = 0

        data = {
            "sum_prepay": sum_prepay,
            "sum_postpay": sum_postpay,
            "bill_sum": order.bill_sum,
            "bill_sum_paid": order.bill_sum_paid,
            "sum_prepay_fact": sum_prepay_fact,
            "sum_postpay_fact": sum_postpay_fact,
        }
        return Response(data, status=status.HTTP_200_OK)

    # добавить дату завершения
    @action(detail=True, methods=["post"], url_path=r"add-date-completed")
    def date_completed(self, request, pk=None, *args, **kwargs):
        data = request.data
        date_completed_data = data["date_completed"]

        date_completed = datetime.datetime.strptime(
            date_completed_data, "%Y-%m-%d"
        ).date()
        order = Order.objects.get(pk=pk)
        order.date_completed = date_completed
        order.status = "COMPLETED"
        order._change_reason = "Ручное"
        order.save()
        data = {}
        return Response(data, status=status.HTTP_200_OK)


class EmailsViewSet(viewsets.ModelViewSet):
    queryset = EmailsCallBack.objects.none()
    serializer_class = EmailsCallBackSerializer
    http_method_names = ["get", "post", "put", "update"]

    @action(detail=False, methods=["post"], url_path=r"call-back-email")
    def send_email_callback(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data, many=False)

        if serializer.is_valid():
            email_obj = serializer.save()
            user_name = serializer.data["name"]
            user_phone = serializer.data["phone"]

            to_manager = os.environ.get("EMAIL_MANAGER_CALLBACK")
            send_code = send_email_message(
                "Обратный звонок",
                f"Имя: {user_name}. Телефон: {user_phone}",
                to_manager,
            )
            if send_code:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path=r"manager-email")
    def send_manager_email(self, request, *args, **kwargs):
        data = request.data

        client_id = data["client_id"]
        text_message = data["text_message"]
        client = Client.objects.get(id=int(client_id))

        title_email = "Сообщение с сайта от клиента"
        text_email = f"Клиент: {client.contact_name}Телефон: {client.phone}Сообщение{text_message}"
        to_manager = client.manager.email
        html_message = loader.render_to_string(
            "core/emails/email.html",
            {
                "client_name": client.contact_name,
                "client_phone": client.phone,
                "text": text_message,
            },
        )
        send_code = send_email_message_html(
            title_email, text_email, to_manager, html_message=html_message
        )
        if send_code:
            return Response("ok", status=status.HTTP_200_OK)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)
