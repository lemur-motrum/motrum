from apps.client.models import Client, Order
from rest_framework import serializers

from apps.client.models import AccountRequisites, Requisites
from apps.specification.api.serializers import ListProductSpecificationSerializer, ListsProductSpecificationSerializer, ProductSpecificationSerializer

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ('password',"date_joined")

class RequisitesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requisites
        fields = "__all__"
        
class AccountRequisitesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountRequisites
        fields = "__all__"
        # exclude = ('requisites',)
        
class AllAccountRequisitesSerializer(serializers.ModelSerializer):
    accountrequisites_set = AccountRequisitesSerializer(read_only=False, many=True)
    class Meta:
        model = Requisites
        exclude = ('client',)

class ClientRequisitesSerializer(serializers.ModelSerializer):
    requisites_set = AllAccountRequisitesSerializer(read_only=False, many=True)
    class Meta:
        model = Client
        exclude = ('password',"date_joined","contact_name","email","first_name","groups","phone","is_active","is_staff","is_superuser","last_login","last_name","user_permissions","username")  


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"      

class LkOrderSerializer(serializers.ModelSerializer):
    status_full = serializers.CharField(source='get_status_display')
    specification_list = ListsProductSpecificationSerializer(source='specification',read_only=True)
    # specification_list = ListProductSpecificationSerializer(source='specification',read_only=True)
    class Meta:
       model = Order
       fields = ('name','client','date_order','specification','cart','requisites','account_requisites','status', 'status_full',"specification_list","bill_sum","bill_sum_paid","bill_file","act_file")
       read_only_fields = ('status_full',)                        

        
   
 