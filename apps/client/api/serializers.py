from apps.client.models import Client
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
        
class AllAccountRequisitesSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    accountrequisites_set = AccountRequisitesSerializer(read_only=True, many=True)
    class Meta:
        model = Requisites
        fields = "__all__"
                
# class AllClientRequisitesSerializer(serializers.ModelSerializer):
#     requisites = RequisitesSerializer(many=True, read_only=True)
    
#     class Meta:
#         model = Client
#         exclude = ('password',"date_joined")
        
   
        
        