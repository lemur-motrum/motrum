from rest_framework import routers, serializers, viewsets, mixins, status
from rest_framework.decorators import action
from apps.product.api.serializers import ProductSerializer
from apps.product.models import Product


class ApiProduct(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    http_method_names = ["get",]
    
    @action(detail=False, methods=['get'])
    def blog_data(self, request):
       pass