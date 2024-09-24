import datetime
from operator import itemgetter
import os
import re
from xmlrpc.client import boolean
from django.conf import settings
from django.db.models import Prefetch
from regex import F
from rest_framework import routers, serializers, viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.cache import cache
from django.contrib.auth import authenticate, login
from django.db.models import Q, F, OrderBy
from django.db.models import Case, When, Value, IntegerField
from apps.notifications.models import Notification

from apps.client.api.serializers import (
    AccountRequisitesSerializer,
    ClientRequisitesSerializer,
    ClientSerializer,
    DocumentSerializer,
    LkOrderSerializer,
    OrderSerializer,
    RequisitesSerializer,
)
from django.contrib.sessions.models import Session
from apps.client.models import (
    STATUS_ORDER,
    STATUS_ORDER_INT,
    AccountRequisites,
    Client,
    Order,
    Requisites,
)
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
                        serializer_prod.skip_history_when_saving = True
                        specification_product = serializer_prod.save()

                    else:
                        return Response(
                            serializer_prod.errors,
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    total_amount += float(item_data["price_all"])
                # # обновить спецификацию пдф

                specification.total_amount = total_amount
                specification.skip_history_when_saving = True
                specification.save()

                pdf = crete_pdf_specification(
                    specification.id, requisites, account_requisites, request
                )
                specification.file = pdf
                specification.skip_history_when_saving = True
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
        cart.is_active = True
        cart.save()

        # client = cart.client
        client = None
        specification = save_specification(data, request)

        data_order = {
            "client": client,
            "name": 123131,
            "specification": specification.id,
            "status": "PROCESSING",
        }

        try:
            order = Order.objects.get(specification=specification)
            serializer = self.serializer_class(order, data=data_order, many=False)
            if serializer.is_valid():
                order = serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            serializer = self.serializer_class(data=data_order, many=False)
            if serializer.is_valid():
                order = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # создание счета к заказу
    @action(detail=True, methods=["update"], url_path=r"create-bill-admin")
    def create_bill_admin(self, request, pk=None, *args, **kwargs):

        order = Order.objects.get(specification_id=pk)

        order.create_bill()

        return Response(None, status=status.HTTP_200_OK)

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

    # страница мои заказов аякс загрузка
    @action(detail=False, url_path="load-ajax-order-list")
    def load_ajax_order_list(self, request):
        from django.db.models.functions import Length

        count = int(request.query_params.get("count"))
        serializer_class = LkOrderSerializer
        current_user = request.user.id
        client = Client.objects.get(pk=current_user)
        
        # сортировки
        sorting = "-id"
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
                    queryset=Notification.objects.filter(
                        type_notification="STATUS_ORDERING", is_viewed=False
                    ),
                    to_attr="filtered_notification_items",
                )
            )
            .order_by(sorting)
        )

        # 
        serializer = serializer_class(orders, many=True)
        data = serializer.data

        notifications = Notification.objects.filter(
            client_id=current_user, type_notification="STATUS_ORDERING", is_viewed=False
        ).update(is_viewed=True)

        if sorting == "-id":
            data = sorted(data, key=lambda x: len(x["notification_set"]), reverse=True)

        data_response = {
            "data": data[count : count + 5],
        }
        return Response(data=data_response, status=status.HTTP_200_OK)


    # страница мои документы аякс загрузка
    @action(detail=False, url_path="load-ajax-document-list")
    def load_ajax_document_list(self, request):
        count = int(request.query_params.get("count"))
        serializer_class = LkOrderSerializer
        current_user = request.user.id
        client = Client.objects.get(pk=current_user)

        # сортировки
        sorting = None
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

        notifications = (
            Notification.objects.filter(client_id=current_user, is_viewed=False)
            .exclude(type_notification="STATUS_ORDERING")
            .update(is_viewed=True)
        )

        data_response = {
            "data": documents[count : count + 10],
            # [count : count + 10]
        }

        return Response(data=data_response, status=status.HTTP_200_OK)
