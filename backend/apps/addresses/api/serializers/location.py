from rest_framework.serializers import ModelSerializer

from apps.addresses.models import Location

LOCATION_FIELDS = ['id', 'customer', 'street_address', 'city', 'state', 'zipcode', 'is_active']


class LocationBaseSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = LOCATION_FIELDS


class LocationReadOnlySerializer(LocationBaseSerializer):
    ...


class LocationWriteSerializer(LocationBaseSerializer):
    class Meta(LocationBaseSerializer.Meta):
        read_only_fields = 'id',

    def create_instance(self):
        return Location(**self.validated_data)
