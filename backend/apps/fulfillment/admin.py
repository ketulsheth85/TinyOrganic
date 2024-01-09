from django.contrib.admin import register

from apps.core.admin import CoreAdmin
from apps.fulfillment.models import (
    FulfillmentCenter as TinyFulfillmentCenter,
    FulfillmentCenterZipcode as TinyFulfillmentCenterZipcode
)


@register(TinyFulfillmentCenter)
class ProductAdmin(CoreAdmin):
    readonly_fields = 'location',
    exclude = 'zipcodes',
    ordering = 'location',
    list_display = 'location',
    search_fields = 'location',


@register(TinyFulfillmentCenterZipcode)
class ProductAdmin(CoreAdmin):
    readonly_fields = 'zipcode',
    ordering = 'warehouses', 'zipcode'
    list_display = 'zipcode', 'fulfillment_centers'
    search_fields = 'zipcode', 'warehouses__location'

    # Optimize list display by prefetching
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('warehouses')

    def fulfillment_centers(self, obj):
        return "\n".join([w.location for w in obj.warehouses.filter()])
