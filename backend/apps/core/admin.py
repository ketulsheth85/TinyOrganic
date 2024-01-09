from django.contrib.admin import register
from django.db import models
from django_json_widget.widgets import JSONEditorWidget
from simple_history.admin import SimpleHistoryAdmin

from apps.core.models import APIRequestLog


class CoreAdmin(SimpleHistoryAdmin):
    readonly_fields = 'id',

    class Meta:
        abstract = True


@register(APIRequestLog)
class APIRequestLogAdmin(CoreAdmin):
    list_display = 'id', 'request_url', 'response_status_code', 'object_type', 'object_id', 'created_at',
    readonly_fields = 'request_headers', 'request_url', 'response_headers',
    formfield_overrides = {
        # fields.JSONField: {'widget': JSONEditorWidget}, # if django < 3.1
        models.JSONField: {'widget': JSONEditorWidget},
    }
    search_fields = 'id', 'request_url', 'object_type', 'object_id', 'response_status_code',
