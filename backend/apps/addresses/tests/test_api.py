from unittest import mock

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.customers.tests.factories.customer import CustomerFactory
from apps.addresses.tests.factories.location import LocationFactory


def _mock_valid_tax_response(self, *args, **kwargs):
    return {
            'valid_address': True,
            'messages': []
        }


class LocationViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.customer = CustomerFactory()

    def test_can_view_location_information_in_json_response_payload(self):
        customer = self.customer
        address = LocationFactory(customer=customer)

        url = reverse('customer-detail', args=[str(customer.id)])
        response = self.client.get(url)

        self.assertDictContainsSubset(
            response.json()['addresses'][0],
            {
                'id': str(address.id),
                'customer': str(customer.id),
                'streetAddress': address.street_address,
                'state': str(address.state),
                'city': address.city,
                'isActive': address.is_active,
                'zipcode': str(address.zipcode)
            }
        )

    @mock.patch(
        'libs.tax_nexus.avalara.client.TaxProcessorClient.validate_tax_address',
        side_effect=_mock_valid_tax_response
    )
    def test_can_update_existing_location(self, *args):
        customer = self.customer
        address = LocationFactory(customer=customer)

        url = reverse('location-detail', args=[str(address.id)])
        response = self.client.patch(url, {
            'city': 'Dallas'
        })

        self.assertEquals(response.json()['city'], 'Dallas')

    def test_can_delete_existing_location(self):
        customer = self.customer
        address = LocationFactory(customer=customer)

        url = reverse('location-detail', args=[str(address.id)])
        response = self.client.delete(url, args=[str(address.id)])

        self.assertEquals(response.status_code, 204)

    @mock.patch(
        'libs.tax_nexus.avalara.client.TaxProcessorClient.validate_tax_address',
        side_effect=_mock_valid_tax_response
    )
    def test_can_add_multiple_addresses_to_customer(self, *args):
        customer = self.customer
        address_one = LocationFactory(customer=customer)
        address_two = LocationFactory(customer=customer)

        url = reverse('customer-detail', args=[str(customer.id)])
        response = self.client.get(url)
        addresses = response.json()['addresses']

        self.assertEqual(any(str(address_one.id) == adr['id'] for adr in addresses), True)
        self.assertEqual(any(str(address_two.id) == adr['id'] for adr in addresses), True)
