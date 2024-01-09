from django.db import models, transaction

from apps.core.models import CoreModel
from apps.webhooks.tasks import subscribe_to_webhook_events


class Webhook(CoreModel):
    name = models.CharField(max_length=120)
    topic = models.CharField(max_length=120)
    endpoint_url = models.URLField()
    is_active = models.BooleanField(default=False)
    format = 'json'

    def __str__(self):
        return f'{self.topic}'

    def _subscribe_to_webhook_topic(self):
        subscribe_to_webhook_events.delay(self.id)

    def save(self, *args, **kwargs):
        if 'is_active' in self.get_dirty_fields() and self.is_active:
            transaction.on_commit(self._subscribe_to_webhook_topic)
        super().save(*args, **kwargs)
