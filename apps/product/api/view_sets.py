import math
from django.db.models import Prefetch
from unicodedata import category
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status
from apps.product.api.serializers import (
    CartSerializer,
    ProductCartSerializer,
    ProductSerializer,
)
from apps.product.models import (
    Cart,
    CategoryProduct,
    GroupProduct,
    Product,
    ProductCart,
    ProductProperty,
)
from django.db.models import Q, F, OrderBy


class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Product.objects.none()
    serializer_class = ProductSerializer
    http_method_names = [
        "get",
    ]

    # аякс загрузка товаров в каталоге
    @action(detail=False, url_path=r"load-ajax-product-list")
    def load_ajax_match_list(self, request, *args, **kwargs):
        count = int(request.query_params.get("count"))

        count_last = 10
        # page_btn = request.query_params.get("addMoreBtn")
        page_btn = request.query_params.get("addMoreBtn").lower() in ("true", "1", "t")

        page_get = request.query_params.get("page")
        sort_price = request.query_params.get("sort")
        # sort_price = "-"
        if request.query_params.get("vendor"):
            vendor_get = request.query_params.get("vendor")
            vendor_get = vendor_get.split(",")
        else:
            vendor_get = None

        category_get = request.query_params.get("category")

        if request.query_params.get("group"):
            groupe_get = request.query_params.get("group")
        else:
            groupe_get = None

        if page_btn == False:
            count = int(count) * int(page_get)

        # сортировка по гет параметрам
        q_object = Q()
        q_object &= Q(check_to_order=True)

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

        queryset = (
            Product.objects.select_related(
                "supplier",
                "vendor",
                "category",
                "group",
                "price",
                "stock",
            )
            .prefetch_related(Prefetch("stock__lot"), Prefetch("productproperty_set"))
            .filter(q_object)
            .order_by(sorting)[count : count + count_last]
        )
        # .order_by(ordering_filter)
        # проверка есть ли еще данные для след запроса
        queryset_next = Product.objects.filter(q_object)[
            count + count_last + 1 : count + count_last + 2
        ].exists()

        serializer = ProductSerializer(
            queryset, context={"request": request}, many=True
        )
        # page_count = queryset.count()

        page_count = Product.objects.filter(q_object).count()

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
        }

        return Response(data=data_response, status=status.HTTP_200_OK)


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.filter()
    serializer_class = CartSerializer
    http_method_names = ["get", "post", "update", "delete"]

    # создать корзину
    @action(detail=False, methods=["get"], url_path=r"add-cart")
    def add_cart(self, request, *args, **kwargs):
        # response = super().create(request, args, kwargs)
        session = request.COOKIES.get("sessionid")
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

        else:
            if request.user.is_staff:
                try:
                    cart = Cart.objects.get(session_key=session, is_active=False)
                    response = Response()
                    response.data = cart.id
                    response.status = status.HTTP_200_OK
                    response.set_cookie("cart", cart.id, max_age=2629800)
                    return response

                except Cart.DoesNotExist:
                    data = {"session_key": session, "save_cart": False, "client": None}
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

                # cart = Cart.objects.get_or_create(session_key=session, save_cart=False)
                # response.set_cookie("cart", cart[0].id, max_age=2629800)
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

        queryset = ProductCart.objects.filter(cart_id=kwargs["cart"])
        serializer_class = ProductCartSerializer
        data = request.data
        if "product_new" in data:
            product_new = data["product_new"]
        else:
            product_new = None
        # обновление товара
        try:
            product = queryset.get(product=data["product"], product_new=product_new)

            data["id"] = product.id

            serializer = serializer_class(product, data=data, many=False)
            if serializer.is_valid():
                cart_product = serializer.save()
                cart_len = ProductCart.objects.filter(cart_id=kwargs["cart"]).count()
                data["cart_len"] = cart_len
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # новый товар
        except ProductCart.DoesNotExist:
            serializer = serializer_class(data=data, many=False)
            if serializer.is_valid():
                cart_product = serializer.save()
                cart_len = ProductCart.objects.filter(cart_id=kwargs["cart"]).count()
                data["cart_len"] = cart_len
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # изменить колличство товаров в корзине
    @action(detail=True, methods=["update"], url_path=r"update-product")
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
        queryset.delete()
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
