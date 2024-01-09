from decimal import Decimal

from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.utils import timezone
from django_fsm import FSMField, transition
from model_utils import Choices
from django.conf import settings

from apps.addresses.models import Location
from apps.orders.libs import (
    OrderFulfillmentStatusEnum,
    OrderPaymentStatusEnum,
    OrderSyncedToShopifyStatusEnum,
    OrderConfirmationEmailStatus,
)
from libs.payment_processors.exceptions import CouldNotChargeOrderError, CouldNotProcessChargeError
from libs.shopify_api_client import ShopifyAPIClient, CouldNotCancelOrderError

from apps.billing.models import PaymentMethod
from apps.core.models import CoreModel
from apps.customers.models import Customer, CustomerChild
from apps.discounts.models import CustomerDiscount
from apps.orders.models import (
    ShippingRate,
)
from apps.orders.tasks import (
    sync_order_to_shopify,
    sync_refunded_order_to_shopify,
    sync_order_to_tax_client,
    sync_refund_to_tax_client,
    sync_partial_refund_to_shopify,
    sync_order_payment_failed_to_analytics,
    send_order_confirmation_email,
    sync_order_placed_event,
    sync_order_to_yotpo,
    sync_refund_to_yotpo,
)


class Order(CoreModel):
    customer = models.ForeignKey(
        to=Customer,
        on_delete=models.PROTECT,
        related_name='orders',
    )
    customer_child = models.ForeignKey(
        to=CustomerChild,
        on_delete=models.PROTECT,
        related_name='orders',
        null=True,
        blank=True,
    )
    external_order_id = models.CharField(max_length=128, null=True, blank=True)
    # status fields
    fulfillment_status = FSMField(
        default=OrderFulfillmentStatusEnum.pending,
        choices=OrderFulfillmentStatusEnum.as_choices(),
    )
    payment_status = FSMField(
        default=OrderPaymentStatusEnum.pending,
        choices=OrderPaymentStatusEnum.as_choices(),
    )
    synced_to_shopify_status = FSMField(
        default=OrderSyncedToShopifyStatusEnum.pending,
        choices=OrderSyncedToShopifyStatusEnum.as_choices(),
    )
    order_confirmation_email_status = FSMField(
        default=OrderConfirmationEmailStatus.unsent,
        choices=OrderConfirmationEmailStatus.as_choices(),
    )
    payment_method = models.ForeignKey(
        to=PaymentMethod,
        on_delete=models.PROTECT,
        related_name='associated_orders',
        null=True,
        blank=True,
    )
    charged_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    refund_reason = models.TextField(
        choices=Choices(
            '',
            'Order Cancellation',
            'Order Issue',
        ),
        default='',
        blank=True
    )
    partial_refund_amount = models.DecimalField(default=Decimal('0'), max_digits=10, decimal_places=2)
    refunded_amount = models.DecimalField(default=Decimal('0'), max_digits=10, decimal_places=2)
    charged_amount = models.DecimalField(default=Decimal('0'), max_digits=10, decimal_places=2)
    discount_amount_total = models.DecimalField(default=Decimal('0'), max_digits=10, decimal_places=2)
    subtotal_amount = models.DecimalField(default=Decimal('0'), max_digits=10, decimal_places=2)
    amount_total = models.DecimalField(default=Decimal('0'), max_digits=10, decimal_places=2)
    tax_total = models.DecimalField(default=Decimal('0'), max_digits=10, decimal_places=2)
    tags = ArrayField(base_field=models.CharField(max_length=256), null=True, blank=True)
    tracking_number = models.CharField(max_length=512, null=True, blank=True)
    order_number = models.TextField(null=True, blank=True)
    shipping_rate = models.ForeignKey(
        to=ShippingRate,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    shipping_address = models.ForeignKey(
        to=Location,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    synced_to_shopify = models.BooleanField(default=False)
    synced_to_avalara = models.BooleanField(default=False)
    synced_to_yotpo = models.BooleanField(default=False)
    applied_discount = models.ForeignKey(
        to=CustomerDiscount,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    payment_processor_charge_id = models.CharField(max_length=256, null=True, blank=True)
    charge_attempts = models.SmallIntegerField(default=0)
    charge_failure_message = models.TextField(blank=True)
    MAX_FAILED_ORDER_CHARGE_ATTEMPTS = 10

    @transition(
        field='payment_status',
        source=[
            OrderPaymentStatusEnum.pending,
        ],
        target=OrderPaymentStatusEnum.paid,
        on_error=OrderPaymentStatusEnum.pending,
        conditions=[lambda order: order.fulfillment_status != OrderFulfillmentStatusEnum.cancelled]
    )
    def charge(self):
        try:
            if self.amount_total > Decimal('0'):
                result = self.payment_method.charge(self.amount_total)
                self.charged_amount = result.amount
                self.payment_processor_charge_id = result.payment_processor_charge_id
            self.charged_at = timezone.now()
            if not self.charged_amount:
                self.charged_amount = Decimal('0')
        except (CouldNotChargeOrderError, CouldNotProcessChargeError) as e:
            self.charge_failure_message = str(e)
            raise

    @transition(
        field='payment_status',
        source=[
            OrderPaymentStatusEnum.pending,
            OrderPaymentStatusEnum.paid,
            OrderPaymentStatusEnum.partially_refunded,
        ],
        target=OrderPaymentStatusEnum.partially_refunded
    )
    def partially_refund(self):
        result = self.payment_method.refund(self.partial_refund_amount, self.payment_processor_charge_id)
        self.refunded_amount += result.amount
        self.refunded_at = timezone.now()

    @transition(
        field='payment_status',
        source=OrderPaymentStatusEnum.paid,
        target=OrderPaymentStatusEnum.refunded,
    )
    def refund(self):
        result = self.payment_method.refund(self.charged_amount, self.payment_processor_charge_id)
        self.refunded_amount = result.amount
        self.refunded_at = timezone.now()

    @transition(
        field='fulfillment_status',
        source=[
            OrderFulfillmentStatusEnum.pending,
            OrderFulfillmentStatusEnum.partially_fulfilled,
            OrderFulfillmentStatusEnum.fulfilled,
        ],
        target=OrderFulfillmentStatusEnum.cancelled,
    )
    def cancel(self):
        client = ShopifyAPIClient()
        try:
            client.cancel_order(self)
        except CouldNotCancelOrderError:
            raise
        self.cancelled_at = timezone.now()

    @transition(
        field='synced_to_shopify_status',
        source=[
            OrderSyncedToShopifyStatusEnum.pending,
            OrderSyncedToShopifyStatusEnum.synced,
        ],
        target=OrderSyncedToShopifyStatusEnum.synced,
    )
    def sync_to_shopify(self):
        sync_order_to_shopify.delay(self.id)

    @transition(
        field='order_confirmation_email_status',
        source=[
            OrderConfirmationEmailStatus.sent,
            OrderConfirmationEmailStatus.unsent,
        ],
        target=OrderConfirmationEmailStatus.sent
    )
    def send_confirmation_email(self):
        send_order_confirmation_email.delay(self.id)

    def _sync_paid_order_transaction(self):
        """
          Creates Celery task to send order to shopify, yotpo, and avalara
        """
        # temporarily disable this and use button in admin until we can get these issues resolved.
        # self.sync_to_shopify()
        if settings.YOTPO_ORDER_SYNC_ENABLED:
            sync_order_to_yotpo.delay(self.id)
        self.send_confirmation_email()
        sync_order_to_tax_client.apply_async(args=(self.id,), countdown=4)

    def _sync_refunded_order_transaction(self):
        sync_refunded_order_to_shopify.delay(self.id)
        sync_refund_to_tax_client.delay(self.id)
        if settings.YOTPO_ORDER_SYNC_ENABLED:
            sync_refund_to_yotpo.delay(self.id)

    def _sync_partial_refunded_order_transaction(self):
        sync_partial_refund_to_shopify.delay(self.id)
        if settings.YOTPO_ORDER_SYNC_ENABLED:
            sync_refund_to_yotpo.delay(self.id)

    def _sync_order_charge_failed_analytics_event(self):
        sync_order_payment_failed_to_analytics.delay(self.id)

    def _mark_discount_as_redeemed(self):
        if self.applied_discount:
            self.applied_discount.redeem()
            self.applied_discount.save()

    def is_24_pack(self):
        recipe_line_items = self.line_items.filter(product__product_type='recipe')
        number_of_recipe_items = sum(line_item.quantity for line_item in recipe_line_items)
        return number_of_recipe_items >= 24

    def save(self, *args, **kwargs):
        if (
            self.charge_attempts >= self.MAX_FAILED_ORDER_CHARGE_ATTEMPTS and
            self.payment_status == str(OrderPaymentStatusEnum.pending)
        ):
            self.payment_status = OrderPaymentStatusEnum.failed
            transaction.on_commit(self._sync_order_charge_failed_analytics_event)
        else:
            if not self.is_new() and self.is_dirty() and 'payment_status' in self.get_dirty_fields():
                if self.payment_status == OrderPaymentStatusEnum.paid:
                    transaction.on_commit(self._sync_paid_order_transaction)
                    transaction.on_commit(self._mark_discount_as_redeemed)
                    sync_order_placed_event.delay(self.id)
                if self.payment_status == OrderPaymentStatusEnum.refunded:
                    transaction.on_commit(self._sync_refunded_order_transaction)
                if self.payment_status == OrderPaymentStatusEnum.partially_refunded:
                    transaction.on_commit(self._sync_partial_refunded_order_transaction)
            # This will catch the case in which multiple partial refunds are applied.
            elif not self.is_new() and self.is_dirty() and 'refunded_at' in self.get_dirty_fields():
                if self.payment_status == OrderPaymentStatusEnum.partially_refunded:
                    transaction.on_commit(self._sync_partial_refunded_order_transaction)

        super().save(*args, **kwargs)
