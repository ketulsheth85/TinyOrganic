import importlib

from django.db import models

from apps.core.models import CoreModel


class PaymentProcessor(CoreModel):
    name = models.CharField(max_length=128, unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'

    @property
    def module(self):
        if self.is_active:
            return importlib.import_module(f'libs.payment_processors.{self.name.lower()}')

    @property
    def client(self):
        if self.is_active:
            return self.module.PaymentProcessorClient()

    @property
    def billing_transaction_manager(self):
        if self.is_active:
            return self.module.BillingTransactionManager
