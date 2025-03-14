from apps.client.models import (
    Client,
    DocumentShipment,
    EmailsAllWeb,
    EmailsCallBack,
    Order,
    PhoneClient,
    RequisitesAddress,
    RequisitesOtherKpp,
)
from rest_framework import serializers

from apps.client.models import AccountRequisites, Requisites
from datetime import date
from apps.notifications.api.serializers import (
    NotificationOrderSerializer,
    NotificationSerializer,
)
from apps.product.api.serializers import CartOktAllSerializer, ProductCartSerializer
from apps.specification.api.serializers import (
    ListProductSpecificationSerializer,
    ListsProductSpecificationSerializer,
    ListsSpecificationSerializer,
    ProductSpecificationSerializer,
    SpecificationSerializer,
)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ("password", "date_joined")


class PhoneClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneClient
        fields = "__all__"


class RequisitesSerializer(serializers.ModelSerializer):
    type_payment_full = serializers.CharField(source="get_type_payment")

    class Meta:
        model = Requisites
        fields = "__all__"


class RequisitesV2Serializer(serializers.ModelSerializer):

    class Meta:
        model = Requisites
        fields = "__all__"


class RequisitesAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequisitesAddress
        fields = "__all__"


class AccountRequisitesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountRequisites
        fields = "__all__"
        # exclude = ('requisites',)


class RequisitesOtherKppSerializer(serializers.ModelSerializer):
    accountrequisites_set = AccountRequisitesSerializer(read_only=False, many=True)

    class Meta:
        model = RequisitesOtherKpp
        fields = "__all__"
        # exclude = ('requisites',)


class AllAccountRequisitesSerializer(serializers.ModelSerializer):
    type_payment_full = serializers.CharField(source="get_type_payment")
    # requisitesotherkpp_set = RequisitesOtherKppSerializer(read_only=False, many=True)
    # accountrequisites_set = AccountRequisitesSerializer(read_only=False, many=True)

    class Meta:
        model = Requisites
        exclude = ("client",)


class RequisitesToOktOrderSerializer(serializers.ModelSerializer):
    type_payment_full = serializers.CharField(source="get_type_payment")
    requisitesotherkpp_set = RequisitesOtherKppSerializer(read_only=False, many=True)

    class Meta:
        model = Requisites
        fields = "__all__"


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
            "requisites_set",
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderSaveCartSerializer(serializers.ModelSerializer):
    specification_list = ListsProductSpecificationSerializer(
        source="specification", read_only=True
    )

    class Meta:
        model = Order
        fields = "__all__"


class LkOrderDocumentShipmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentShipment
        fields = (
            "id",
            "date",
            "file",
            "order",
        )

    def to_representation(self, instance):
        representation = super(
            LkOrderDocumentShipmentSerializer, self
        ).to_representation(instance)
        if instance.date:
            representation["date"] = instance.date.strftime("%d.%m.%Y")

        return representation


class LkOrderSerializer(serializers.ModelSerializer):
    status_full = serializers.CharField(source="get_status_display", read_only=True)
    requisites_full = RequisitesSerializer(source="requisites", read_only=True)
    specification_list = ListsProductSpecificationSerializer(
        source="specification", read_only=True
    )
    url = serializers.CharField(source="get_absolute_url_web", read_only=True)
    # notification_set = NotificationSerializer(source='filtered_notification_items',read_only=False, many=True)
    notification_count = serializers.CharField()
    documentshipment_set = LkOrderDocumentShipmentSerializer(read_only=True, many=True)

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
            "bill_name",
            "bill_sum",
            "bill_sum_paid",
            "bill_file",
            "bill_date_start",
            "bill_date_stop",
            "act_file",
            # "notification_set",
            "notification_count",
            "url",
            "documentshipment_set",
            "id_bitrix",
        )
        read_only_fields = ("status_full",)

    def to_representation(self, instance):
        representation = super(LkOrderSerializer, self).to_representation(instance)
        if representation["bill_date_start"]:
            representation["bill_date_start"] = instance.bill_date_start.strftime(
                "%d.%m.%Y"
            )
            representation["bill_date_stop"] = instance.bill_date_stop.strftime(
                "%d.%m.%Y"
            )
        return representation


class LkOrderDocumentSerializer(serializers.ModelSerializer):
    status_full = serializers.CharField(source="get_status_display")
    requisites_full = RequisitesSerializer(source="requisites", read_only=True)
    specification_list = ListsSpecificationSerializer(
        source="specification", read_only=True
    )
    documentshipment_set = LkOrderDocumentShipmentSerializer(read_only=True, many=True)
    notification_set = NotificationSerializer(
        source="filtered_notification_items", read_only=False, many=True
    )

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
            "bill_name",
            "notification_set",
            "documentshipment_set",
        )
        read_only_fields = ("status_full",)

    def to_representation(self, instance):
        representation = super(LkOrderDocumentSerializer, self).to_representation(
            instance
        )
        if representation["bill_date_start"]:
            representation["bill_date_start"] = instance.bill_date_start.strftime(
                "%d.%m.%Y"
            )
            representation["bill_date_stop"] = instance.bill_date_stop.strftime(
                "%d.%m.%Y"
            )
        return representation


class OrderOktSerializer(serializers.ModelSerializer):
    specification_list = SpecificationSerializer(source="specification", read_only=True)
    bill_status = serializers.SerializerMethodField()
    name_req_full = serializers.CharField(source="requisites")
    status_full = serializers.CharField(source="get_status_display")
    requisites_set = AllAccountRequisitesSerializer(
        source="requisites",
        read_only=False,
    )
    cart_list = CartOktAllSerializer(source="cart", read_only=False)
    is_superuser = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = "__all__"

    def get_bill_status(self, obj):

        if obj.bill_date_stop:
            if date.today() > obj.bill_date_stop:
                return False
            else:
                return True
        else:
            return None

    def get_is_superuser(self, obj):

        user = self.context.get("request").user
        if user.is_superuser:
            return True
        else:
            return False

    def to_representation(self, instance):
        representation = super(OrderOktSerializer, self).to_representation(instance)
        if instance.bill_date_stop:
            representation["bill_date_stop"] = instance.bill_date_stop.strftime(
                "%d.%m.%Y"
            )
        if instance.bill_date_start:
            representation["bill_date_start"] = instance.bill_date_start.strftime(
                "%d.%m.%Y"
            )
        if instance.date_completed:
            representation["date_completed"] = instance.date_completed.strftime(
                "%d.%m.%Y"
            )
        if instance.requisites:
            representation["name_req_full"] = instance.requisites.legal_entity

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


class EmailsCallBackSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailsCallBack
        fields = "__all__"


class EmailsAllWebSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailsAllWeb
        fields = "__all__"
