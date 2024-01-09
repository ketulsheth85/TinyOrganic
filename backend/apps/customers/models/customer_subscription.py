import datetime
from datetime import timedelta

from django.template.loader import render_to_string
from django.db import models, transaction
from django.utils import timezone
from django_fsm import FSMField, transition
from model_utils import Choices
from sentry_sdk.utils import logger

from apps.core.models import CoreModel
from apps.customers.models import Customer, CustomerChild
from apps.customers.models.validators.customer_subscription import validate_charge_date
from apps.customers.tasks import (
    sync_subscription_cancelled_event,
    sync_subscription_activated_event,
    sync_subscription_created_event,
)
from apps.customers.tasks.recurring import _send_email


class SubscriptionStatusEnum:
    active = 'active'
    inactive = 'inactive'
    paused = 'paused'


class CustomerSubscription(CoreModel):
    customer = models.ForeignKey(
        to=Customer,
        on_delete=models.PROTECT,
        related_name='subscriptions',
    )
    customer_child = models.OneToOneField(
        to=CustomerChild,
        related_name='subscription',
        on_delete=models.PROTECT,
    )
    number_of_servings = models.PositiveSmallIntegerField(default=12)
    frequency = models.PositiveSmallIntegerField(choices=Choices(1, 2, 4), default=2)
    next_order_changes_enabled_date = models.DateField(null=True, blank=True)
    next_order_charge_date = models.DateField(null=True, blank=True, validators=[validate_charge_date, ])
    is_active = models.BooleanField(default=False)
    activated_at = models.DateTimeField(null=True, blank=True)
    paused_at = models.DateTimeField(null=True, blank=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    # todo: remove after 2 weeks of production deployment. this is a temporary measure to ensure that our
    #  lists/segments in klaviyo are updated with the latest
    synced_to_klaviyo = models.BooleanField(default=False)
    updated_profile_fields_to_klaviyo = models.BooleanField(default=False)
    status = FSMField(
        choices=Choices(SubscriptionStatusEnum.active, SubscriptionStatusEnum.inactive, SubscriptionStatusEnum.paused),
        default=SubscriptionStatusEnum.inactive,
    )

    def __str__(self):
        return f'{self.customer_child}, {self.number_of_servings} cups every {self.frequency} week(s)'

    @property
    def line_items(self):
        return self.customer_child.cart.line_items.filter()

    @property
    def amount(self):
        return sum([line_item.product_variant.price * line_item.quantity for line_item in self.line_items])

    def _create_order(self):
        from apps.orders.libs import OrderBuilder
        OrderBuilder.from_subscription(self)

    def update_next_order_dates(self):
        self.next_order_charge_date = timezone.now().date() + timedelta(days=self.frequency * 7)
        self.next_order_changes_enabled_date = self.next_order_charge_date - timedelta(days=1)

    @transition(
        field='status',
        source=[
            SubscriptionStatusEnum.inactive,
            SubscriptionStatusEnum.paused
        ],
        target=SubscriptionStatusEnum.active,
        on_error=SubscriptionStatusEnum.inactive,
    )
    def activate(self, create_order: bool = True):
        if create_order:
            try:
                self._create_order()
            except Exception:
                raise
        self.is_active = True
        self.activated_at = timezone.now()
        self.update_next_order_dates()

    @transition(
        field='status',
        source=SubscriptionStatusEnum.active,
        target=SubscriptionStatusEnum.paused,
        on_error=SubscriptionStatusEnum.active
    )
    def pause(self, next_order_charge_date=None):
        self.is_active = False
        self.paused_at = timezone.now()

        if next_order_charge_date:
            self.next_order_charge_date = next_order_charge_date
            self.next_order_changes_enabled_date = next_order_charge_date - timedelta(days=1)
        else:
            self.update_next_order_dates()

    @transition(
        field='status',
        source=[
            SubscriptionStatusEnum.active,
            SubscriptionStatusEnum.paused,
        ],
        target=SubscriptionStatusEnum.inactive,
        on_error=SubscriptionStatusEnum.active,
    )
    def deactivate(self):
        self.deactivated_at = timezone.now()
        self.is_active = False
        self.next_order_charge_date = None
        self.next_order_changes_enabled_date = None

    def _send_subscription_cancellation_notification(self):
        subject = 'Your subscription has been cancelled from Tiny Organics'
        context = {'first_name': self.customer.first_name}
        html_body = render_to_string('emails/customer_subscription/subscription-cancelled.html', context)
        text_body = ''
        try:
            _send_email(
                subject,
                text_body,
                html_body,
                self.customer.email,
            )
        except Exception as e:
            logger.error(e)

        sync_subscription_cancelled_event.delay(self.id)

    def _send_subscription_activated_event(self):
        sync_subscription_activated_event.delay(self.id)

    def _sync_new_subscription_to_segment(self):
        sync_subscription_created_event.delay(self.id)

    def save(self, *args, **kwargs):
        changed_fields = self.get_dirty_fields()
        # when number of servings change, ensure the cart line items contain the appropriate skus
        if self.number_of_servings and 'number_of_servings' in changed_fields:
            if int(self.number_of_servings) < 24:
                transaction.on_commit(lambda: self.customer_child.cart.line_items.filter().delete())

        if self.is_new():
            transaction.on_commit(self._sync_new_subscription_to_segment)
        if not self.is_new() and 'is_active' in changed_fields:
            # new customers should not be affected by this. only existing ones
            if not self.is_active:
                transaction.on_commit(self._send_subscription_cancellation_notification)
            else:
                transaction.on_commit(self._send_subscription_activated_event)

        if self.is_active and self.next_order_charge_date:
            next_order_charge_date = self.next_order_charge_date
            if type(self.next_order_charge_date) == str:
                next_order_charge_date = datetime.datetime.strptime(next_order_charge_date, '%Y-%m-%d')

            if 'next_order_charge_date' in changed_fields:
                self.next_order_changes_enabled_date = next_order_charge_date - timedelta(days=1)
            else:
                self.next_order_changes_enabled_date = None

            if not self.next_order_changes_enabled_date:
                self.next_order_changes_enabled_date = next_order_charge_date - timedelta(days=1)

        super().save(*args, **kwargs)
