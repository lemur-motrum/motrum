from apps.client.models import Client, Order
from rest_framework import serializers

from apps.client.models import AccountRequisites, Requisites

from apps.notifications.api.serializers import NotificationOrderSerializer, NotificationSerializer
from apps.specification.api.serializers import (
    ListProductSpecificationSerializer,
    ListsProductSpecificationSerializer,
    ListsSpecificationSerializer,
    ProductSpecificationSerializer,
)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ("password", "date_joined")


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
        exclude = ("client",)


class ClientRequisitesSerializer(serializers.ModelSerializer):
    requisites_set = AllAccountRequisitesSerializer(read_only=False, many=True)

    class Meta:
        model = Client
        exclude = (
            "password",
            "date_joined",
            "contact_name",
            "email",
            "first_name",
            "groups",
            "phone",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "last_name",
            "user_permissions",
            "username",
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class LkOrderSerializer(serializers.ModelSerializer):
    status_full = serializers.CharField(source="get_status_display")
    requisites_full = RequisitesSerializer(source="requisites", read_only=True)
    specification_list = ListsProductSpecificationSerializer(
        source="specification", read_only=True
    )
    
    # notification_set = NotificationSerializer(source='filtered_notification_items',read_only=False, many=True)
    notification_count =  serializers.CharField()
    
    class Meta:
        model = Order
        fields = (
            "id",
            "name",
            "client",
            "date_order",
            "specification",
            "cart",
            "requisites",
            "requisites_full",
            "account_requisites",
            "status",
            "status_full",
            "specification_list",
            "bill_sum",
            "bill_sum_paid",
            "bill_file",
            "bill_date_start",
            "bill_date_stop",
            "act_file",
            # "notification_set",
            "notification_count",
            
        )
        read_only_fields = ("status_full",)
        
    def to_representation(self, instance):
        representation = super(LkOrderSerializer, self).to_representation(instance)
        if representation['bill_date_start']:
            representation['bill_date_start'] = instance.bill_date_start.strftime('%d.%m.%Y')
            representation['bill_date_stop'] = instance.bill_date_stop.strftime('%d.%m.%Y')
        return representation    
    
    
class LkOrderDocumentSerializer(serializers.ModelSerializer):
    status_full = serializers.CharField(source="get_status_display")
    requisites_full = RequisitesSerializer(source="requisites", read_only=True)
    specification_list = ListsSpecificationSerializer(
        source="specification", read_only=True
    )
    notification_set = NotificationSerializer(source='filtered_notification_items',read_only=False, many=True)
    
    
    class Meta:
        model = Order
        fields = (
            "id",
            "name",
            "client",
            "date_order",
            "specification",
            "cart",
            "requisites",
            "requisites_full",
            "account_requisites",
            "status",
            "status_full",
            "specification_list",
            "bill_sum",
            "bill_sum_paid",
            "bill_file",
            "bill_date_start",
            "bill_date_stop",
            "bill_date_start",
            "notification_set",
            
        )
        read_only_fields = ("status_full",)
        
    def to_representation(self, instance):
        representation = super(LkOrderDocumentSerializer, self).to_representation(instance)
        if representation['bill_date_start']:
            representation['bill_date_start'] = instance.bill_date_start.strftime('%d.%m.%Y')
            representation['bill_date_stop'] = instance.bill_date_stop.strftime('%d.%m.%Y')
        return representation    
    


class DocumentSerializer(serializers.Serializer):
    """Your data serializer, define your fields here."""
    name = serializers.CharField()
    cart = serializers.CharField()
    status = serializers.CharField()
    status_full = serializers.CharField()
    pdf = serializers.CharField()
    requisites_contract = serializers.CharField()
    requisites_legal_entity = serializers.CharField()
    date_created = serializers.DateField()
    data_stop = serializers.DateField()
    amount = serializers.FloatField()
