import datetime
import os
import re
from django.conf import settings
from regex import F
from rest_framework import routers, serializers, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.contrib.auth import authenticate, login

from apps.client.api.serializers import (
    AccountRequisitesSerializer,
    AllAccountRequisitesSerializer,
    ClientRequisitesSerializer,
    ClientSerializer,
    OrderSerializer,
    RequisitesSerializer,
)
from django.contrib.sessions.models import Session
from apps.client.models import AccountRequisites, Client, Order, Requisites
from apps.core.utils import (
    create_time_stop_specification,
    get_presale_discount,
    save_specification,
)
from apps.core.utils_web import (
    _get_pin,
    _verify_pin,
    get_product_item_data,
    send_email_message,
    send_pin,
)
from apps.product.models import Cart, Price, Product, ProductCart
from apps.specification.api.serializers import (
    ProductSpecificationSerializer,
    SpecificationSerializer,
)
from apps.specification.utils import crete_pdf_specification


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
                        if cart_id:
                            Cart.objects.filter(id=cart_id).update(client=client)
                        return Response(serializer.data, status=status.HTTP_200_OK)
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
        
            

        # сохранение спецификации для заказа с реквизитами
        if "requisites" in data:
            print(data["requisites"])
            extra_discount = client.percent
            # сохранение спецификации
            products_cart = ProductCart.objects.filter(cart_id=cart)
            serializer_class_specification = SpecificationSerializer
            data_stop = create_time_stop_specification()
            data_specification = {
                "cart": cart.id,
                "admin_creator": client.manager.id,
                "id_bitrix": None,
                "date_stop": data_stop,
            }

            serializer = serializer_class_specification(
                data=data_specification, partial=True
            )
            if serializer.is_valid():
                serializer.skip_history_when_saving = True
                specification = serializer.save()

                # сохранение продуктов для спецификации
                total_amount = 0
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
                        serializer_prod.skip_history_when_saving = True
                        specification_product = serializer_prod.save()

                    else:
                        return Response(
                            serializer_prod.errors,
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    total_amount += int(item_data["price_all"])
                # # обновить спецификацию пдф
                specification.total_amount = total_amount
                specification.skip_history_when_saving = True
                specification.save()

                pdf = crete_pdf_specification(specification.id)
                specification.file = pdf
                specification.skip_history_when_saving = True
                specification.save()
                specification = specification.id
                requisites =  data["requisites"]
                account_requisites =  data["account_requisites"]
                status_order = "PAYMENT"

            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # сохранение заказа БЕЗ реквизитами
        else:
            specification = None
            status_order = "PROCESSING"
            requisites = None
            account_requisites = None
            
       

        serializer_class = OrderSerializer
        data_order = {
            "client": client,
            "name": 123131,
            "specification": specification,
            "cart": cart.id,
            "status": status_order,
            "requisites": requisites,
            "account_requisites": account_requisites,
        }
        serializer = self.serializer_class(data=data_order, many=False)
        if serializer.is_valid():
            order = serializer.save()
            
            cart.is_active = True
            cart.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # сохранение спецификации дмин специф
    @action(detail=False, methods=["post"], url_path=r"add-order-admin")
    def add_order_admin(self, request, *args, **kwargs):
        data = request.data
        cart = Cart.objects.get(id=data["cart"])
        cart.is_active = True
        cart.save()

        client = cart.client
        specification = save_specification(data)

        data_order = {
            "client": client,
            "name": 123131,
            "specification": specification.id,
            "status": "PAYMENT",
        }
        try:
            order = Order.objects.get(specification=specification)
            serializer = self.serializer_class(order, data=data, many=False)
            if serializer.is_valid():
                order = serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            serializer = self.serializer_class(data=data, many=False)
            if serializer.is_valid():
                order = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # изменение спецификации дмин специф
    @action(detail=True, methods=["update"], url_path=r"update-order-admin")
    def update_order_admin(self, request, pk=None, *args, **kwargs):
        data = request.data
        cart = Cart.objects.filter(id=data["cart"]).update(is_active=False)

        return Response(cart, status=status.HTTP_200_OK)

    # выйти и з изменения без сохранения спецификации дмин специф
    @action(detail=False, methods=["get"], url_path=r"exit-order-admin")
    def exit_order_admin(self, request, *args, **kwargs):
        cart_id = request.COOKIES.get("cart")
        cart = Cart.objects.filter(id=cart_id).update(is_active=True)

        return Response(cart, status=status.HTTP_200_OK)
