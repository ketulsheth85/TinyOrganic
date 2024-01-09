from rest_framework.routers import SimpleRouter

from apps.webhooks.api.viewsets import WebhookEventViewSet

webhook_router = SimpleRouter()
webhook_router.register('webhook-event', WebhookEventViewSet)
