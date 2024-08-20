from apps.client.models import Cart, Client, ProductCart
from rest_framework import serializers

from apps.client.models import AccountRequisites, Requisites

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
                  
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"
        
class ProductCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCart
        fields = "__all__"        
       
        
   
        
        