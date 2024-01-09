from django.urls import reverse
from rest_framework.test import APITestCase


class WebhookEventAPITestSuite(APITestCase):
    def test_will_reject_post_request_when_signature_is_not_included(self):
        url = reverse('webhookevent-list')
        response = self.client.post(url, {}, format='json')
        self.assertEquals(403, response.status_code)
