import base64
import math
import os
import traceback
from django.db.models import Max
from django.db.models import Prefetch
from unicodedata import category
from django.forms import CharField
from apps.supplier.models import Vendor
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status
from apps.client.models import Order
from apps.core.utils import check_file_price_directory_exist, product_cart_in_file, serch_products_web
from apps.logs.utils import error_alert
from apps.product.api.serializers import (
    CartSerializer,
    ProductCartSerializer,
    ProductSearchSerializer,
    ProductSerializer,
    VendorSearchSerializer,
)
from apps.product.models import (
    Cart,
    CategoryProduct,
    GroupProduct,
    Price,
    Product,
    ProductCart,
    ProductProperty,
)
from django.db.models import Q, F, OrderBy, Value

from apps.specification.models import ProductSpecification
import threading

from apps.specification.utils import save_nomenk_doc
from apps.supplier.get_utils.motrum_storage import get_motrum_storage
from project.settings import MEDIA_ROOT
import datetime
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes, authentication_classes
from django.contrib.postgres.search import SearchVector, SearchQuery


class ProductViewSet(viewsets.ModelViewSet):
    # permission_classes = (permissions.AllowAny,)
    queryset = Product.objects.none()
    serializer_class = ProductSerializer
    http_method_names = [
        "get",
        "post",
    ]

    # аякс загрузка товаров в каталоге
    @action(detail=False, url_path=r"load-ajax-product-list")
    def load_ajax_match_list(self, request, *args, **kwargs):
        count = int(request.query_params.get("count"))
        print(request)
        count_last = 10
        # page_btn = request.query_params.get("addMoreBtn")
        page_btn = request.query_params.get("addMoreBtn").lower() in ("true", "1", "t")

        page_get = request.query_params.get("page")
        sort_price = request.query_params.get("sort")
        price_none = request.query_params.get("pricenone")
        price_to = float(request.query_params.get("priceto"))
        price_from = float(request.query_params.get("pricefrom"))

        if request.query_params.get("search_text"):
            search_text = request.query_params.get("search_text")
            if search_text == "":
                search_text = None
        else:
            search_text = None
            
        print("search_text",search_text)

        # sort_price = "-"
        if request.query_params.get("vendor"):
            vendor_get = request.query_params.get("vendor")
            vendor_get = vendor_get.split(",")
        else:
            vendor_get = None
        print(vendor_get)
        category_get = request.query_params.get("category")

        if request.query_params.get("group"):
            groupe_get = request.query_params.get("group")
        else:
            groupe_get = None

        if page_btn == False:
            count = int(count) * int(page_get)

        # сортировка по гет параметрам
        q_object = Q()
        q_object &= Q(check_to_order=True, in_view_website=True)
        

        if vendor_get is not None:
            if "None" in vendor_get:
                if len(vendor_get) > 1:
                    vendor_get.remove("None")
                    q_object &= Q(
                        vendor__slug=None,
                    ) | Q(vendor__slug__in=vendor_get)
                else:
                    q_object &= Q(vendor__slug=None)
            else:
                q_object &= Q(vendor__slug__in=vendor_get)

        if category_get is not None:
            if category_get == "all":
                q_object &= Q(article__isnull=False)
            elif category_get == "other":
                q_object &= Q(category=None)
            elif category_get == "":
                pass
            elif category_get == "search":
                q_object &= Q(article__isnull=False)
            else:
                q_object &= Q(category__id=category_get)

        if groupe_get is not None:
            q_object &= Q(group__id=groupe_get)

        # сортировка по цене
        if sort_price:
            if sort_price == "?":
                # sorting = "?"
                sorting = F("id").asc(nulls_last=True)
            elif sort_price == "ASC":
                sorting = F("price__rub_price_supplier").asc(nulls_last=True)
            else:
                sorting = F("price__rub_price_supplier").desc(nulls_last=True)

        # сортировка из блока с ценами

        if price_none == "true":
            q_object &= Q(price__rub_price_supplier__isnull=False)

        if price_from != 0:
            q_object &= Q(price__rub_price_supplier__gte=price_from)

        if price_to != 0:
            q_object &= Q(price__rub_price_supplier__lte=price_to)

        # if sort_price:
        #     sort = "price__rub_price_supplier"
        #     ordering_filter = OrderBy(
        #         F(sort.lstrip("-")),
        #         descending=sort_price.startswith("-"),
        #         nulls_last=True,
        #     )
        # else:
        #     sort = "price__rub_price_supplier"
        #     ordering_filter = OrderBy(
        #         F(sort.lstrip("-")),
        #         descending="-".startswith("-"),
        #         nulls_last=True,
        #     )
        print(q_object)
        queryset = (
            Product.objects.select_related(
                "supplier",
                "vendor",
                "category",
                "group",
                "price",
                "stock",
            )
            .prefetch_related(
                Prefetch("stock__lot"),
                Prefetch("productproperty_set"),
                Prefetch("productimage_set"),
                Prefetch("productimage_set"),
            )
            .filter(q_object)
            # .order_by(sorting)[count : count + count_last]
        )
       
        # поиск
        print(queryset)
        if search_text:
            queryset = serch_products_web(search_text, queryset)
            
        
        # проверка есть ли еще данные для след запроса
        # queryset_next = Product.objects.filter(q_object)[
        #     count + count_last : count + count_last + 1
        # ].exists()
        queryset_next = queryset[
            count + count_last : count + count_last + 1
        ].exists()
        # prod_qs = Product.objects.filter(q_object)
       
        price_max = queryset.aggregate(Max("price__rub_price_supplier", default=0))
        page_count = queryset.count()
        queryset = queryset.order_by(sorting)[count : count + count_last]
        
        serializer = ProductSerializer(
            queryset, context={"request": request}, many=True
        )
        
        if page_count % 10 == 0:
            count = page_count / 10
        else:
            count = math.trunc(page_count / 10) + 1

        if page_count <= 20:
            small = True
        else:
            small = False

        data_response = {
            "data": serializer.data,
            "next": queryset_next,
            "count": math.ceil(page_count / 10),
            "page": page_get,
            "small": small,
            "price_max": price_max,
        }

        return Response(data=data_response, status=status.HTTP_200_OK)

    # поиск товар в окт
    @action(detail=False, methods=["post", "get"], url_path=r"search-product")
    def search_product(self, request, *args, **kwargs):
        data = request.data
        count = data["count"]
        count_last = data["count_last"]
        search_input = data["search_text"]
        search_input = search_input.replace(".", "").replace(",", "")
        search_input = search_input.split()

        print(search_input)
        # # вариант ищет каждое слово все рабоатет
        queryset = Product.objects.filter(
            
            Q(name__icontains=search_input[0])
            # | Q(article__icontains=search_input[0])
            | Q(article_supplier__icontains=search_input[0])
            | Q(additional_article_supplier__icontains=search_input[0])
            | Q(description__icontains=search_input[0])
        )
        print(len(search_input))
        # del search_input[0]
        if len(search_input) > 1:
            for search_item in search_input[1:]:
                queryset = queryset.filter(
                    Q(name__icontains=search_item)
                    # | Q(article__icontains=search_item)
                    | Q(article_supplier__icontains=search_item)
                    | Q(additional_article_supplier__icontains=search_item)
                    | Q(description__icontains=search_input)
                )
        else:
            queryset = queryset.filter(check_to_order=True).order_by("name")
        queryset = queryset.filter(check_to_order=True).order_by("name")
        
        queryset = queryset[count  : count_last ]
        # стандатный варинт ищет целиокм

        # queryset = Product.objects.filter(
        #     Q(name__icontains=search_input)
        #     | Q(article__icontains=search_input)
        #     | Q(article_supplier__icontains=search_input)
        #     | Q(additional_article_supplier__icontains=search_input)
        # )
        page_count = queryset.count()
        count_all = count + page_count
        serializer = ProductSearchSerializer(queryset, many=True)
        data_response = {
            "data": serializer.data,
            "count": count,
            "count_all": count_all,
        }
        return Response(data_response, status=status.HTTP_200_OK)

    @authentication_classes([BasicAuthentication])
    @permission_classes([IsAuthenticated])
    @action(
        detail=False,
        methods=["post", "get"],
        authentication_classes=[BasicAuthentication],
        permission_classes=[IsAuthenticated],
        url_path="get-1c-nomenclature",
    )
    def get_nomenclature(self, request, *args, **kwargs):
        print("get_nomenclature")

        data = request.data
        try:
            path, tr, e = save_nomenk_doc(data["file"])
            print(path)
            if path == "ERROR":

                data_resp = {"result": "error", "error": f"info-error {tr}{e}"}
                error = "file_api_error"
                location = "Получение\сохранение данных складов 1с "
                info = f"Получение\сохранение данных складов 1с . Тип ошибки:{e}{tr} DATA из 1с -  {data}"
                e = error_alert(error, location, info)
                return Response(data_resp, status=status.HTTP_400_BAD_REQUEST)
            else:
                get_motrum_storage(path)
                data_resp = {"result": "ok", "error": None}
                return Response(data_resp, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            tr = traceback.format_exc()
            error = "file_api_error"
            location = "Получение\сохранение данных складов 1с "
            info = f"Получение\сохранение данных складов 1с . Тип ошибки:{e}{tr} DATA из 1с -  {data}"
            e = error_alert(error, location, info)
            data_resp = {"result": "error", "error": f"info-error {info}"}
            return Response(data_resp, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post", "get"], url_path=r"search-product-web")
    def search_product_web(self, request, *args, **kwargs):
        data = request.data
        count = data["count"]
        count_last = data["count_last"]
        search_input = data["search_text"]
        search_input = search_input.replace(".", "").replace(",", "")
        search_input = search_input.split()

        print(search_input)
        # # вариант ищет каждое слово все рабоатет
        queryset = Product.objects.filter(
            
            Q(name__icontains=search_input[0])
            # | Q(article__icontains=search_input[0])
            | Q(article_supplier__icontains=search_input[0])
            | Q(additional_article_supplier__icontains=search_input[0])
            | Q(description__icontains=search_input[0])
           
        )
        print(len(search_input))
        # del search_input[0]
        if len(search_input) > 1:
            for search_item in search_input[1:]:
                queryset = queryset.filter(
                    Q(name__icontains=search_item)
                    # | Q(article__icontains=search_item)
                    | Q(article_supplier__icontains=search_item)
                    | Q(additional_article_supplier__icontains=search_item)
                    | Q(description__icontains=search_item)
                )
        else:
            queryset = queryset.filter(check_to_order=True).filter(in_view_website=True).order_by("name")
        
        queryset = queryset.filter(check_to_order=True).filter(in_view_website=True).order_by("name")
        
        queryset = queryset[count  : count_last ]
        print(queryset)
        # стандатный варинт ищет целиокм
        # queryset = Product.objects.filter(
        #     Q(name__icontains=search_input)
        #     | Q(article__icontains=search_input)
        #     | Q(article_supplier__icontains=search_input)
        #     | Q(additional_article_supplier__icontains=search_input)
        # )
        page_count = queryset.count()
        count_all = count + page_count
        serializer = ProductSearchSerializer(queryset, many=True)
        data_response = {
            "data": serializer.data,
            "count": count,
            "count_all": count_all,
        }
        return Response(data_response, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post", "get"], url_path=r"search-vendor")
    def search_vendor(self, request, *args, **kwargs):
        
        data = request.data
        print(data)
        count = int(data["count"])
        count_last = int(data["count_last"])
        search_input = data["search_text"]
        # search_input = search_input.replace(".", "").replace(",", "")
        # search_input = search_input.split()

        
        # стандатный варинт ищет целиокм
        queryset = Vendor.objects.filter(
             Q(name__icontains=search_input)
        )
        print(queryset)
    
        page_count = queryset.count()

        count_all = count + page_count
        serializer = VendorSearchSerializer(queryset, many=True)
        data_response = {
            "data": serializer.data,
            "count": count,
            "count_all": count_all,
        }
        return Response(data_response, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post", "get"], url_path=r"search-product-okt-categ")
    def search_product_okt_categ(self, request, *args, **kwargs):
        data = request.data
        count = data["count"]
        count_last = data["count_last"]
        search_input = data["search_text"]
        search_input = search_input.replace(".", "").replace(",", "")
        search_input = search_input.split()
        
        # q_object = Q(name__icontains=search_input[0])
        # q_object |= Q(article_supplier__icontains=search_input[0])
        # q_object |= Q(additional_article_supplier__icontains=search_input[0])
        # q_object |= Q(description__icontains=search_input[0])
        
        if "cat" in data and data["cat"] != "" :
            category_id = int(data["cat"])
        else:
            category_id = None
        
        if "gr" in data and data["gr"] != "":
            group_id = int(data["gr"])
           
        else:
            group_id = None
        print(search_input)
        # # вариант ищет каждое слово все рабоатет
      
        
        
        
        
        queryset = Product.objects.filter(
            
            Q(name__icontains=search_input[0])
            # | Q(article__icontains=search_input[0])
            | Q(article_supplier__icontains=search_input[0])
            | Q(additional_article_supplier__icontains=search_input[0])
            | Q(description__icontains=search_input[0])
        )
        print(len(search_input))
        # del search_input[0]
        if len(search_input) > 1:
            for search_item in search_input[1:]:
           
                queryset = queryset.filter(
                    Q(name__icontains=search_item)
                    # | Q(article__icontains=search_item)
                    | Q(article_supplier__icontains=search_item)
                    | Q(additional_article_supplier__icontains=search_item)
                    | Q(description__icontains=search_input)
                )
        else:
            queryset = queryset.filter(check_to_order=True).order_by("name")
        
        q_object = Q(check_to_order=True)
        if category_id:
            q_object &= Q(category_id=category_id)
        if group_id:
            q_object &= Q(group_id=group_id)
        
        print(q_object)
        queryset = queryset.filter(q_object).order_by("name")
        
        queryset = queryset[count  : count_last ]

        page_count = queryset.count()
        count_all = count + page_count
        serializer = ProductSearchSerializer(queryset, many=True)
        data_response = {
            "data": serializer.data,
            "count": count,
            "count_all": count_all,
        }
        return Response(data_response, status=status.HTTP_200_OK)

class CartViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cart.objects.filter()
    serializer_class = CartSerializer
    http_method_names = ["get", "post", "delete"]

    # создать корзину
    @action(detail=False, methods=["get", "post"], url_path=r"add-cart")
    def add_cart(self, request, *args, **kwargs):
        print("add_cart")
        data = request.data
        # response = super().create(request, args, kwargs)

        session = request.COOKIES.get("sessionid")
        # корзина юзера анонимного
        if request.user.is_anonymous:
            if session == None:

                request.session.create()
                session = request.session.session_key

                data = {"session_key": session, "save_cart": False, "client": None}
                serializer = self.serializer_class(data=data, many=False)
                if serializer.is_valid():
                    serializer.save()
                    response = Response()
                    response.data = serializer.data["id"]
                    response.status = status.HTTP_201_CREATED
                    response.set_cookie(
                        "sessionid", serializer.data["session_key"], max_age=2629800
                    )
                    response.set_cookie("cart", serializer.data["id"], max_age=2629800)
                    return response
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                try:
                    cart = Cart.objects.get(session_key=session, save_cart=False)
                    response.set_cookie("cart", cart.id, max_age=2629800)
                    response = Response()
                    response.status = status.HTTP_200_OK
                    return response

                except Cart.DoesNotExist:
                    data = {"session_key": session, "save_cart": False, "client": None}
                    serializer = self.serializer_class(data=data, many=False)
                    if serializer.is_valid():
                        serializer.save()
                        response = Response()
                        response.data = serializer.data["id"]
                        response.status = status.HTTP_201_CREATED
                        response.set_cookie(
                            "sessionid", serializer.data["session_key"], max_age=2629800
                        )
                        response.set_cookie(
                            "cart", serializer.data["id"], max_age=2629800
                        )

                        return response
                    else:
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )
        # корзина админов и логин юзера
        else:
            # корзина админов
            bitrix_id_order = False
            iframe = False
            if request.method == "POST":
                data = request.data
                if data["iframe"]:
                    iframe = True
            print(iframe)

            if request.user.is_staff:
                cart = None
                if iframe:
                    bitrix_id_order = request.COOKIES["bitrix_id_order"]
                    print(bitrix_id_order)
                    if bitrix_id_order:
                        print("if bitrix_id_order")
                        try:
                            order = Order.objects.get(id_bitrix=int(bitrix_id_order))
                            print(order)
                            cart = order.cart
                            print(cart)
                        except Order.DoesNotExist:
                            print(Order.DoesNotExist)
                            cart = None
                # try:
                # cart = Cart.objects.filter(session_key=session, is_active=False).last()

                if cart:
                    response = Response()
                    response.data = cart.id
                    response.status = status.HTTP_200_OK
                    # response.set_cookie(
                    #     "cart", cart.id, max_age=2629800, samesite="None", secure=True
                    # )
                    response.set_cookie(
                        "cart",
                        cart,
                        max_age=2629800,
                        samesite="None",
                        secure=True,
                    )
                    response.set_cookie(
                        "order",
                        order.id,
                        max_age=2629800,
                        samesite="None",
                        secure=True,
                    )
                    response.set_cookie(
                        "type_save",
                        "update",
                        max_age=2629800,
                        samesite="None",
                        secure=True,
                    )
                    response.set_cookie(
                        "specificationId",
                        order.specification,
                        max_age=2629800,
                        samesite="None",
                        secure=True,
                    )

                    return response

                else:

                    # except Cart.DoesNotExist:
                    data = {
                        "session_key": session,
                        "save_cart": False,
                        "client": None,
                        "cart_admin": request.user,
                    }
                    serializer = self.serializer_class(data=data, many=False)
                    if serializer.is_valid():
                        serializer.save()
                        response = Response()
                        response.data = serializer.data["id"]
                        response.status = status.HTTP_201_CREATED
                        # response.set_cookie(
                        #     "sessionid", serializer.data["session_key"], max_age=2629800
                        # )
                        response.set_cookie(
                            "cart",
                            serializer.data["id"],
                            max_age=2629800,
                            samesite="None",
                            secure=True,
                        )
                        response.set_cookie(
                            "type_save",
                            "new",
                            max_age=2629800,
                            samesite="None",
                            secure=True,
                        )

                        return response
                    else:
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )

            # cart = Cart.objects.get_or_create(session_key=session, save_cart=False)
            # response.set_cookie("cart", cart[0].id, max_age=2629800)
            # корзина юзера логиненого
            else:
                try:
                    cart = Cart.objects.get(client=request.user, is_active=False)

                    response = Response()
                    response.data = cart.id
                    response.status = status.HTTP_200_OK
                    response.set_cookie("cart", cart.id, max_age=2629800)
                    return response

                except Cart.DoesNotExist:

                    data = {
                        "session_key": session,
                        "save_cart": False,
                        "client": request.user,
                    }

                    serializer = self.serializer_class(data=data, many=False)

                    if serializer.is_valid():
                        serializer.save()
                        response = Response()
                        response.data = serializer.data["id"]
                        response.status = status.HTTP_201_CREATED
                        # response.set_cookie(
                        #     "sessionid", serializer.data["session_key"], max_age=2629800
                        # )
                        response.set_cookie(
                            "cart", serializer.data["id"], max_age=2629800
                        )

                        return response
                    else:
                        return Response(
                            serializer.errors, status=status.HTTP_400_BAD_REQUEST
                        )

    # добавить товар в корзину
    @action(detail=False, methods=["post"], url_path=r"(?P<cart>\w+)/save-product")
    def add_product_cart(self, request, *args, **kwargs):
        print(111111111111)
        queryset = ProductCart.objects.filter(cart_id=kwargs["cart"])
        print(queryset)
        serializer_class = ProductCartSerializer
        data = request.data
        # товар без записи в окт
        if "product_new" in data:
            product_new = data["product_new"]
            product_price = None
            product_sale_motrum = None
        # товар из окт
        else:
            product_price_okt = Price.objects.get(prod=data["product"])
            product_price = product_price_okt.rub_price_supplier
            if product_price_okt.sale:
                product_sale_motrum = product_price_okt.sale.percent
            else:
                product_sale_motrum = None

            product_new = None

            # data["product_price"] =
        # обновление товара
        print(data["product"])
        print(queryset)
        try:
            product = queryset.get(product=data["product"], product_new=product_new)
            print(product)
            data["id"] = product.id
            serializer = serializer_class(product, data=data, many=False)
            if serializer.is_valid():
                cart_product = serializer.save()
                cart_len = ProductCart.objects.filter(cart_id=kwargs["cart"]).count()
                data["cart_len"] = cart_len
                cart_prod = ProductCart.objects.get(
                    cart_id=kwargs["cart"], product=data["product"]
                )
                data["cart_prod"] = cart_prod.id
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # новый товар
        except ProductCart.DoesNotExist:
            # try:
            #     product = queryset.get(product=data["product"])
            #     data = {"status": "product_in_cart"}
            #     return Response(data, status=status.HTTP_409_CONFLICT)
            
            # except ProductCart.DoesNotExist:
            
            data["product_price"] = product_price
            data["product_sale_motrum"] = product_sale_motrum
            serializer = serializer_class(data=data, many=False)
            if serializer.is_valid():
                cart_product = serializer.save()
                cart_len = ProductCart.objects.filter(cart_id=kwargs["cart"]).count()
                data["cart_len"] = cart_len
                cart_prod = ProductCart.objects.get(
                    cart_id=kwargs["cart"], product=data["product"]
                )
                data["cart_prod"] = cart_prod.id
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # добавить товар не из  бд в корзину
    @action(detail=False, methods=["post"], url_path=r"(?P<cart>\w+)/save-product-new")
    def add_product_cart_new(self, request, *args, **kwargs):

        serializer_class = ProductCartSerializer
        data = request.data
        cart_id = data["cart"]
        product_new_article = data["product_new_article"]
        try:
            product_okt = Product.objects.get(
                vendor_id=data["vendor"], article_supplier=product_new_article
            )
            data = {"status": "product_in_okt"}
            return Response(data, status=status.HTTP_409_CONFLICT)
        except Product.DoesNotExist:
            try:
                product_new_article = ProductCart.objects.get(
                    cart_id=cart_id, product_new_article=product_new_article
                )
                data = {"status": "product_in_cart"}
                return Response(data, status=status.HTTP_409_CONFLICT)

            except ProductCart.DoesNotExist:
                
                serializer = serializer_class(data=data, many=False)
                if serializer.is_valid():
                    cart_product = serializer.save()
                    cart_len = ProductCart.objects.filter(
                        cart_id=kwargs["cart"]
                    ).count()
                    data["cart_len"] = cart_len
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

    @action(detail=True, methods=["post"], url_path=r"upd-product-new")
    def upd_product_cart_new(self, request, pk=None, *args, **kwargs):
        queryset = ProductCart.objects.get(pk=pk)
        serializer_class = ProductCartSerializer

        data = request.data
        serializer = serializer_class(queryset, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path=r"upd-product-cart")
    def upd_product_cart(self, request, pk=None, *args, **kwargs):
        queryset = ProductCart.objects.get(pk=pk)
        serializer_class = ProductCartSerializer

        data = request.data
        if data["product_sale_motrum"] == "":
            data["product_sale_motrum"] = 0
            
        
            
        serializer = serializer_class(queryset, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # изменить количество товаров в корзине
    @action(detail=True, methods=["get", "post"], url_path=r"update-product")
    def update_product_cart(self, request, pk=None, *args, **kwargs):
        queryset = ProductCart.objects.get(pk=pk)
        serializer_class = ProductCartSerializer

        data = request.data
        serializer = serializer_class(queryset, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # удалить товар ИЗ корзине
    @action(detail=True, methods=["delete"], url_path=r"delete-product")
    def delete_product_cart(self, request, pk=None, *args, **kwargs):

        queryset = ProductCart.objects.get(pk=pk)
        if queryset.product_new:
            try:
                prod_spes = ProductSpecification.objects.get(
                    specification__cart=queryset.cart, product_new=queryset.product_new
                )
                prod_spes.delete()
            except ProductSpecification.DoesNotExist:
                pass

        queryset.delete()
        return Response(None, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="cart-file-download")
    def product_cart_in_file_download(self, request, pk=None, *args, **kwargs):
        print("product_cart_in_file_download", request.data)
        cart = 298
        new_dir = "{0}/{1}/{2}".format(MEDIA_ROOT, "documents", "kp_file")
        path_kp = f"{new_dir}/КП.xlsx"

        # cart = 667
        def background_task():
            # Долгосрочная фоновая задача
            product_cart_in_file(path_kp, cart)

        daemon_thread = threading.Thread(target=background_task)
        daemon_thread.setDaemon(True)
        daemon_thread.start()
        stop_daemon = daemon_thread.join()
        # is_alive_daemon = daemon_thread.is_alive()
        return Response(None, status=status.HTTP_200_OK)


# class ProductViewSet(viewsets.ModelViewSet):
#     permission_classes = (permissions.AllowAny,)
#     queryset = Product.objects.none()
#     serializer_class = ProductSerializer
#     http_method_names = ['get', 'head', 'options']

#     @action(detail=False, url_path='load-ajax-product-list')
#     def load_ajax_match_list(self, request):
#         count = int(request.query_params.get('count'))

#         queryset = Product.objects.select_related(
#             "supplier",
#             "vendor",
#             "category_supplier_all",
#             "group_supplier",
#             "category_supplier",
#             "category",
#             "group",
#             "price",
#             "stock",
#         ).filter(check_to_order=True)[count+1:count+2]

#         serializer = ProductSerializer(queryset, many=True)
#         print(serializer.data)

#         return Response(serializer.data)

#     @action(detail=False, url_path=r"view")
#     def view(self, request):
#         queryset = Product.objects.select_related(
#             "supplier",
#             "vendor",
#             "category_supplier_all",
#             "group_supplier",
#             "category_supplier",
#             "category",
#             "group",
#             "price",
#             "stock",
#         ).filter(check_to_order=True)

#         serializer = ProductSerializer(queryset, many=True)
#         print(1231123123)
#         print(serializer.data)

#         return Response(serializer.data)


# class ApiCProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.filter(article="0017")
#     serializer_class = ProductTestSerializer

#     http_method_names = ["get", "post", "put", "update"]

#     @action(detail=False, methods=["get"], url_path=r"1")
#     def one(self, request, *args, **kwargs):
#         queryset = Product.objects.get(article="0017")
#         serializer_class = ProductTestSerializer
#         serializer = self.serializer_class(queryset, many=False)

#         return Response(serializer.data, status=status.HTTP_200_OK)
