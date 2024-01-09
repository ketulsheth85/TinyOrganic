from django.contrib.admin import register

from django.db import models
from django_json_widget.widgets import JSONEditorWidget

from apps.core.admin import CoreAdmin
from apps.webhooks.models import Webhook, WebhookEvent


@register(Webhook)
class WebhookAdmin(CoreAdmin):
    ...


@register(WebhookEvent)
class WebhookEventAdmin(CoreAdmin):
    list_display = 'id', 'webhook', 'is_processed', 'created_at', 'modified_at',
    readonly_fields = 'id', 'webhook', 'is_processed', 'created_at', 'modified_at',
    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {'widget': JSONEditorWidget},
    }
