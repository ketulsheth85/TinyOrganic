from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from apps.customers.models import Customer

CUSTOMER_FIELDS = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'status', 'guardian_type', ]


class CustomerBaseSerializer(ModelSerializer):
    class Meta:
        model = Customer
        fields = CUSTOMER_FIELDS


class CustomerReadOnlySerializer(CustomerBaseSerializer):
    children = SerializerMethodField()
    addresses = SerializerMethodField()
    has_password = SerializerMethodField()

    class Meta(CustomerBaseSerializer.Meta):
        fields = CUSTOMER_FIELDS + ['children', 'has_active_subscriptions', 'addresses', 'subscriptions',
                                    'has_password', ]
        read_only_fields = fields
        depth = 1

    def get_has_password(self, obj):
        return obj.has_usable_password() if obj else False

    def get_children(self, obj):
        from apps.customers.api.serializers import CustomerChildReadOnlySerializer
        if obj.is_authenticated:
            return [CustomerChildReadOnlySerializer(obj.child).data for obj.child in obj.children.filter()]
        return []

    def get_addresses(self, obj):
        from apps.addresses.api.serializers import LocationReadOnlySerializer
        if obj.is_authenticated:
            return [LocationReadOnlySerializer(obj.child).data for obj.child in obj.addresses.filter()]
        return []

    def get_subcriptions(self, obj):
        from apps.customers.api.serializers import CustomerSubscriptionReadOnlySerializer
        if obj.is_authenticated:
            return [CustomerSubscriptionReadOnlySerializer(obj.child).data for obj.child in obj.subscription.filter()]
        return []


class CustomerWriteSerializer(CustomerReadOnlySerializer):
    class Meta(CustomerReadOnlySerializer.Meta):
        read_only_fields = 'id', 'password', 'children', 'addresses', 'subscriptions', 'has_password',
