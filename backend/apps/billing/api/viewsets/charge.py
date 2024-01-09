from rest_framework import mixins, viewsets

from apps.billing.api.serializers.charge import ChargeReadOnlySerializer, ChargeWriteSerializer
from apps.billing.models.charge import Charge


class ChargeViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
	queryset = Charge.objects.filter()
	serializers_class = ChargeReadOnlySerializer

	def get_serializer_class(self):
		if self.request.method == 'POST':
			return ChargeWriteSerializer
		
		return ChargeReadOnlySerializer
