from django.contrib import admin
from django.contrib.admin import register
from fsm_admin.mixins import FSMTransitionMixin

from apps.core.admin import CoreAdmin
from apps.orders.models import Order, OrderLineItem, ShippingRate


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    extra = 0


@register(Order)
class OrderAdmin(FSMTransitionMixin, CoreAdmin):
    fsm_field = 'payment_status', 'synced_to_shopify_status', 'order_confirmation_email_status',
    ordering = '-created_at',
    inlines = OrderLineItemAdminInline,
    list_display = (
        'id',
        'customer',
        'external_order_id',
        'order_number',
        'payment_status',
        'fulfillment_status',
        'tracking_number',
        'subtotal_amount',
        'charged_amount',
        'discount_amount_total',
        'amount_total',
        'refund_reason',
        'charged_at'
    )
    raw_id_fields = 'customer', 'customer_child', 'payment_method', 'applied_discount', 'shipping_address'
    search_fields = 'id', 'customer__email', 'external_order_id', 'refund_reason'

    def get_queryset(self, request):
        return Order.objects.filter().prefetch_related(
            'customer',
            'customer_child',
            'payment_method',
            'applied_discount',
        )

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        extra_fields = [
            'created_at',
            'modified_at',
            'charged_at',
            'charged_amount',
            'refunded_amount',
            'applied_discount',
            'external_order_id',
            'refunded_at',
            'order_number',
            'payment_processor_charge_id',
            'charge_failure_message',
            'synced_to_shopify_status',
            'order_confirmation_email_status',
        ]

        if obj:
            from apps.orders.libs import OrderPaymentStatusEnum
            if obj.payment_status in (OrderPaymentStatusEnum.refunded, OrderPaymentStatusEnum.partially_refunded):
                extra_fields.append('refund_reason')

        return fields + tuple(extra_fields)


@register(ShippingRate)
class ShippingRateAdmin(CoreAdmin):
    list_display = 'id', 'title', 'price', 'is_active', 'is_default'
