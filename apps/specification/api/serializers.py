from rest_framework import serializers

from apps.specification.models import ProductSpecification, Specification

        
class SpecificationSerializer(serializers.ModelSerializer):
    # date = serializers.DateField(format="%Y-%m-%d")
    # date_update = serializers.DateField(format="%Y-%m-%d")
    # date_stop = serializers.DateField(format="%Y-%m-%d")
    class Meta:
        model = Specification
        fields = "__all__"
        
class ProductSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecification
        fields = "__all__"        
       