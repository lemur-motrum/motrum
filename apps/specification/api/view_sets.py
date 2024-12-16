from unicodedata import category
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status

from django.db.models import Q, F, OrderBy

from apps.specification.api.serializers import SpecificationSerializer
from apps.specification.models import Specification


class SpecificationViewSet(viewsets.ModelViewSet):
    queryset = Specification.objects.none()
    serializer_class = SpecificationSerializer
    http_method_names = [
        "get",
    ]

    # @action(
    #     detail=False,
    #     url_path=r"load-ajax-product-list"
    # )
    # def load_ajax_match_list(self, request, *args, **kwargs):

    #     return Response(data=data_response, status=status.HTTP_200_OK)


# class CartViewSet(viewsets.ModelViewSet):
#     queryset = Cart.objects.filter()
#     serializer_class = CartSerializer
#     http_method_names = ["get", "post", "update","delete"]

#     @action(detail=False, methods=["get"], url_path=r"add-cart")
#     def add_cart(self, request, *args, **kwargs):
#         # response = super().create(request, args, kwargs)
#         session = request.COOKIES.get("sessionid")
#         if request.user.is_anonymous:
#             if session == None:
#                 # session = request.session._get_or_create_session_key()
#                 request.session.create()
#                 session = request.session.session_key
#                 # response.set_cookie("sessionid", session, max_age=2629800)
#                 data = {"session_key": session, "save_cart": False, "client": None}
#                 serializer = self.serializer_class(data=data, many=False)
#                 if serializer.is_valid():
#                     serializer.save()
#                     response = Response()
#                     response.data = serializer.data["id"]
#                     response.status = status.HTTP_201_CREATED
#                     response.set_cookie(
#                         "sessionid", serializer.data["session_key"], max_age=2629800
#                     )
#                     response.set_cookie("cart", serializer.data["id"], max_age=2629800)
#                     return response
#                 else:
#                     return Response(
#                         serializer.errors, status=status.HTTP_400_BAD_REQUEST
#                     )
#             else:
#                 try:
#                     cart = Cart.objects.get(session_key=session, save_cart=False)
#                     response.set_cookie("cart", cart.id, max_age=2629800)
#                     response = Response()
#                     response.status = status.HTTP_200_OK
#                     return response

#                 except Cart.DoesNotExist:
#                     data = {"session_key": session, "save_cart": False, "client": None}
#                     serializer = self.serializer_class(data=data, many=False)
#                     if serializer.is_valid():
#                         serializer.save()
#                         response = Response()
#                         response.data = serializer.data["id"]
#                         response.status = status.HTTP_201_CREATED
#                         response.set_cookie(
#                             "sessionid", serializer.data["session_key"], max_age=2629800
#                         )
#                         response.set_cookie(
#                             "cart", serializer.data["id"], max_age=2629800
#                         )
#                         return response
#                     else:
#                         return Response(
#                             serializer.errors, status=status.HTTP_400_BAD_REQUEST
#                         )

#         else:
#             if request.user.is_staff:
#                 try:
#                     cart = Cart.objects.get(session_key=session, save_cart=False)
#                     response = Response()
#                     response.data = cart.id
#                     response.status = status.HTTP_200_OK
#                     response.set_cookie(
#                             "cart", cart.id, max_age=2629800
#                         )
#                     return response

#                 except Cart.DoesNotExist:
#                     data = {"session_key": session, "save_cart": False, "client": None}
#                     serializer = self.serializer_class(data=data, many=False)
#                     if serializer.is_valid():
#                         serializer.save()
#                         response = Response()
#                         response.data = serializer.data["id"]
#                         response.status = status.HTTP_201_CREATED
#                         # response.set_cookie(
#                         #     "sessionid", serializer.data["session_key"], max_age=2629800
#                         # )
#                         response.set_cookie(
#                             "cart", serializer.data["id"], max_age=2629800
#                         )
#                         return response
#                     else:
#                         return Response(
#                             serializer.errors, status=status.HTTP_400_BAD_REQUEST
#                         )

#                 # cart = Cart.objects.get_or_create(session_key=session, save_cart=False)
#                 # response.set_cookie("cart", cart[0].id, max_age=2629800)
#             else:
#                 try:
#                     cart = Cart.objects.get(client=request.user, save_cart=False)
#                     response = Response()
#                     response.data = cart.id
#                     response.status = status.HTTP_200_OK
#                     response.set_cookie(
#                             "cart", cart.id, max_age=2629800
#                         )
#                     return response

#                 except Cart.DoesNotExist:
#                     data = {"session_key": None, "save_cart": False, "client": request.user}
#                     serializer = self.serializer_class(data=data, many=False)
#                     if serializer.is_valid():
#                         serializer.save()
#                         response = Response()
#                         response.data = serializer.data["id"]
#                         response.status = status.HTTP_201_CREATED
#                         # response.set_cookie(
#                         #     "sessionid", serializer.data["session_key"], max_age=2629800
#                         # )
#                         response.set_cookie(
#                             "cart", serializer.data["id"], max_age=2629800
#                         )
#                         return response
#                     else:
#                         return Response(
#                             serializer.errors, status=status.HTTP_400_BAD_REQUEST
#                         )
#                 # cart = Cart.objects.get_or_create(client=request.user, save_cart=False)
#                 # response.set_cookie("cart", cart[0].id, max_age=2629800)

#     @action(detail=False, methods=["post"], url_path=r"(?P<cart>\w+)/save-product")
#     def add_product_cart(self, request, *args, **kwargs):
#         print(kwargs["cart"])
#         queryset = ProductCart.objects.filter(cart_id=kwargs["cart"])
#         serializer_class = ProductCartSerializer
#         data = request.data
#         # обновление товара
#         try:
#             product = queryset.get(product=data["product"])
#             print(product)
#             data["id"] = product.id

#             serializer = serializer_class(product, data=data, many=False)
#             if serializer.is_valid():
#                 cart_product = serializer.save()
#                 cart_len = ProductCart.objects.filter(cart_id=kwargs["cart"]).count()
#                 return Response(cart_len, status=status.HTTP_200_OK)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         # новый товар
#         except ProductCart.DoesNotExist:
#             serializer = serializer_class(data=data, many=False)
#             if serializer.is_valid():
#                 cart_product = serializer.save()
#                 cart_len = ProductCart.objects.filter(cart_id=kwargs["cart"]).count()
#                 return Response(cart_len, status=status.HTTP_200_OK)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @action(detail=True, methods=["update"], url_path=r"update-product")
#     def update_product_cart(self, request, pk=None, *args, **kwargs):
#         queryset = ProductCart.objects.get(pk=pk)
#         serializer_class = ProductCartSerializer

#         data = request.data
#         serializer = serializer_class(queryset, data=data, partial=True)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:

#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     @action(detail=True, methods=["delete"], url_path=r"delete-product")
#     def delete_product_cart(self, request, pk=None, *args, **kwargs):
#         queryset = ProductCart.objects.get(pk=pk)
#         queryset.delete()

#         return Response(None, status=status.HTTP_200_OK)
