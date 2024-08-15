from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.product.api.serializers import ProductSerializer
from apps.product.models import Product


class ProductViewSet(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = Product.objects.none()
    serializer_class = ProductSerializer
    http_method_names = ['get', 'head', 'options']

    @action(detail=False, url_path='load-ajax-product-list')
    def load_ajax_match_list(self, request):
        count = int(request.query_params.get('count'))

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
        ).filter(check_to_order=True)[count+1:count+2]

        serializer = ProductSerializer(queryset, many=True)

        return Response(serializer.data)
