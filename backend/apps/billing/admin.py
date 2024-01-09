from django.contrib.admin import register

from apps.billing.models import (
    Charge,
    PaymentMethod,
    PaymentProcessor,
    Refund,
)
from apps.core.admin import CoreAdmin


@register(PaymentProcessor)
class PaymentProcessorAdmin(CoreAdmin):
    ...


@register(PaymentMethod)
class PaymentMethodAdmin(CoreAdmin):
    raw_id_fields = 'customer', 'payment_processor',
    list_display = (
        'id',
        'customer',
        'last_four',
        'is_valid',
        'setup_for_future_charges',
        'created_at',
        'modified_at',
    )
    search_fields = 'id', 'customer__email', 'payment_processor__name',


@register(Charge)
class ChargeMethodAdmin(CoreAdmin):
    list_display = 'id', 'amount', 'payment_processor_charge_id', 'customer', 'created_at',
    raw_id_fields = 'payment_method', 'customer',
    search_fields = 'customer__email',

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        return fields + ('payment_processor_charge_id', 'status', 'amount',)


@register(Refund)
class RefundAdmin(CoreAdmin):
    search_fields = 'payment_processor_refund_id', 'customer__email'
