from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import routers, serializers, viewsets, mixins, status
from apps.product.api.serializers import ProductSerializer, ProductTestSerializer
from apps.product.models import Product, ProductProperty


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


class ApiCProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(article="0017")
    serializer_class = ProductTestSerializer

    http_method_names = ["get", "post", "put", "update"]

    @action(detail=False, methods=["get"], url_path=r"1")
    def one(self, request, *args, **kwargs):
        queryset = Product.objects.get(article="0017")
        serializer_class = ProductTestSerializer
        serializer = self.serializer_class(queryset, many=False)

        return Response(serializer.data, status=status.HTTP_200_OK)


# чистаю функция юры
class ProductViewSet(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Product.objects.none()
    serializer_class = ProductTestSerializer
    http_method_names = ["get", "head", "options"]

    @action(detail=False, url_path="load-ajax-product-list")
    def load_ajax_match_list(self, request):
        count = int(request.query_params.get("count"))
        vendor = request.query_params.get("vendor")

        queryset = Product.objects.select_related(
            "supplier",
            "vendor",
            "category_supplier_all",
            "group_supplier",
            "category_supplier",
            "category",
            "group",
            "price",
            "stock",
        ).filter(check_to_order=True, vendor=1)[count + 1 : count + 11]

        queryset_next = (
            Product.objects.select_related()
            .filter(check_to_order=True, vendor=1)[count + 12 : count + 13]
            .exists()
        )
        print(queryset_next)

        serializer = ProductTestSerializer(queryset, many=True)
        data_response = {
            "data": serializer.data,
            "next": queryset_next,
        }
        return Response(data=data_response, status=status.HTTP_200_OK)
