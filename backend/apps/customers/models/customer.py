from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from model_utils import Choices
from apps.core.models import CoreModel

from .libs import CustomerManager, PersonMixin
from apps.customers.tasks.loyalty import create_loyalty_customer, update_to_loyalty_client
from apps.orders.libs import OrderPaymentStatusEnum


class Customer(PersonMixin, CoreModel, AbstractUser):
    payment_provider_customer_id = models.TextField(unique=True, blank=True, null=True)
    external_customer_id = models.CharField(max_length=256, db_index=True, blank=True, null=True)
    recharge_customer_id = models.CharField(max_length=256, blank=True, null=True)
    email = models.EmailField(unique=True)
    first_name = models.TextField()
    last_name = models.TextField(blank=True)
    phone_number = models.TextField(blank=True)
    guardian_type = models.TextField(
        choices=Choices(
            'parent',
            'parent_and_expecting',
            'expecting',
            'caregiver',
            'other',
        ),
        default='parent',
    )
    status = models.TextField(
        choices=Choices(
            'lead',
            'plan_selection',
            'checkout',
            'subscriber',
            'deactivated',
        ),
        default='lead',
    )
    has_active_subscriptions = models.BooleanField(default=False)
    username = None
    objects = CustomerManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = 'first_name', 'last_name', 'password'

    def __str__(self) -> str:
        return f'{self.full_name} - {self.email}'

    def active_subscriptions(self):
        return self.subscriptions.filter(is_active=True)

    def _sync_customer_to_loyalty_client(self):
        update_to_loyalty_client(self)

    def _create_loyalty_customer(self):
        create_loyalty_customer(self)

    @property
    def number_of_orders(self):
        return self.orders.filter(
            payment_status__in=[
                OrderPaymentStatusEnum.paid,
                OrderPaymentStatusEnum.partially_refunded,
                OrderPaymentStatusEnum.refunded,
            ]
        ).count()

    @property
    def amount_spent(self):
        paid_orders = self.orders.filter(payment_status=OrderPaymentStatusEnum.paid)
        paid_order_amounts = list(paid_orders.values_list('charged_amount', flat=True))
        return sum(paid_order_amounts)

    def save(self, *args, **kwargs):
        if not self.has_active_subscriptions and self.active_subscriptions().exists():
            self.has_active_subscriptions = True

        if self.is_new():
            transaction.on_commit(self._create_loyalty_customer)
        else:
            if set(["email", "first_name", "last_name"]).intersection(set(self.get_dirty_fields())):
                transaction.on_commit(self._sync_customer_to_loyalty_client)

        super().save(*args, **kwargs)
