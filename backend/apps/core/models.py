import json
import uuid

from dirtyfields import DirtyFieldsMixin
from django.db import models
from simple_history.models import HistoricalRecords


# Create your models here.
class CoreModel(DirtyFieldsMixin, models.Model):
    id = models.UUIDField(
        auto_created=True,
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        serialize=False,
        verbose_name='ID'
    )
    created_at = models.DateTimeField(
        auto_created=True,
        auto_now_add=True,
        db_index=True,
    )
    modified_at = models.DateTimeField(
        auto_created=True,
        auto_now=True,
        db_index=True,
        verbose_name='last modified at',
    )
    history = HistoricalRecords(inherit=True)

    def is_new(self) -> bool:
        return self._state.adding

    class Meta:
        abstract = True
        
        
class APIRequestLogManager(models.Manager):
    def create_from_logged_request(self, request):
        json_payload = json.dumps({})
        if request.body and type(request.body) == dict:
            json_payload = json.dumps(request.body)

        logged_request = self.create(
            request_url=request.url,
            request_headers=request.headers,
            request_json_payload=json.loads(json_payload) if request.body else '{}',
            response_status_code=request.response.status_code,
            response_headers=request.response.headers,
            response_json_payload=json.loads(request.response.raw_body) if request.response.raw_body else '{}',
            object_type=request.object_type,
            object_id=request.object_id,
        )
        return logged_request


class APIRequestLog(CoreModel):
    """
    This model is meant to log every outbound HTTP(s) request to 3rd party services such as Shopify, ReCharge, etc.
    """
    request_url = models.TextField(null=True, blank=True)
    request_headers = models.TextField(null=True, blank=True)
    request_json_payload = models.JSONField(default=dict, null=True, blank=True)
    response_status_code = models.PositiveIntegerField(null=True, blank=True)
    response_headers = models.TextField(null=True, blank=True)
    response_json_payload = models.JSONField(default=dict, null=True, blank=True)
    object_type = models.CharField(max_length=1024, null=True, blank=True, db_index=True)
    object_id = models.CharField(max_length=1024, null=True, blank=True, db_index=True)

    objects = APIRequestLogManager()

    def __str__(self):
        return f'{self.request_url}'
