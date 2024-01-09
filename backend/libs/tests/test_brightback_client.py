import uuid
from unittest import mock
from rest_framework.test import APITestCase

from libs.brightback_client import BrightBackClient

from apps.customers.tests.factories import CustomerFactory, CustomerSubscriptionFactory


class CancellationFlowAPIClientTestSuite(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.customer = CustomerFactory()
        cls.subscription = CustomerSubscriptionFactory(customer=cls.customer)
        cls.session_id = uuid.uuid4()
        cls.cancellationClient = BrightBackClient(cls.subscription, str(cls.session_id))

    def test_can_create_url_for_customer(self):
        response_url = self.cancellationClient.get_cancellation_url()
        self.assertEqual(response_url, 'https://brightback.com/fake_session')
