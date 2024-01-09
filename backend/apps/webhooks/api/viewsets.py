import base64
import hashlib
import hmac

from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, mixins, viewsets
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from apps.webhooks.models import WebhookEvent, Webhook


class WebhookEventIsVerified(BasePermission):
    """
    This is a permission class intended to verify the signature of the webhook event. This will help in preventing
    random bots and/or attackers from bogging our system with random requests to the webhook endpoint. As such,
    no further action is taken after the webhook event request is rejected by this permission class.

    A future improvement would be to log the rejected requests and watch out for attackers so that we can block
    them by ip range and/or region. That component of the system should be logged via some middleware.
    """

    def computed_hmac(self, secret, body):
        hash_code = hmac.new(secret.encode('utf-8'), body, hashlib.sha256)
        return base64.b64encode(hash_code.digest()).decode()

    def verify_hmac(self, secret, body, shopify_hmac):
        return self.computed_hmac(secret, body) == shopify_hmac

    def has_permission(self, request, view):
        return self.verify_hmac(
            settings.SHOPIFY_API_KEY_SECRET,
            request.body,
            request.headers.get('X-Shopify-Hmac-SHA256')
        )


class WebhookEventViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = WebhookEventIsVerified,
    authentication_classes = []
    queryset = WebhookEvent.objects.filter()

    @method_decorator(csrf_exempt)
    def create(self, request, *args, **kwargs):
        WebhookEvent.objects.create(
            webhook=Webhook.objects.get(
                topic=request.headers.get('X-Shopify-Topic'),
            ),
            data=request.data,
            external_id=request.headers.get('X-Shopify-Webhook-Id'),
        )
        return Response({}, status=status.HTTP_200_OK)
