from django.db import models

from apps.core.models import CoreModel
from apps.webhooks.models import Webhook


class WebhookEvent(CoreModel):
    webhook = models.ForeignKey(
        to=Webhook,
        on_delete=models.PROTECT,
        related_name='events',
    )
    data = models.JSONField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    # stores the shopify webhook event id - used for idempotency.
    external_id = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return f'{self.webhook} - {"Processed" if self.is_processed else "Not Processed"}'
