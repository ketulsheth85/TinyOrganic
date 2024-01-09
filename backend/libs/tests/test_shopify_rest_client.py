from unittest import mock

import requests.models
from django.test import TestCase
from libs.shopify_rest_client import ShopifyRestClient, CustomerRequestDTO


class MockedLoggedRequest:
    def __init__(self, paginated=False):
        self.response = requests.models.Response()
        if paginated:
            self.response.headers['Link'] = '''
                <https://tiny-organics.myshopify.com/admin/api/2022-01/customers.json?limit=50&page_info=nextPageData>; 
                rel="next"
            '''


def _mock_requests_session_get(*args, **kwargs):
    response = requests.models.Response()
    response.status_code = 200
    return response


def _mock_requests_session_get_with_headers(*args, **kwargs):
    response = requests.models.Response()
    response.status_code = 200
    response.headers['Link'] = '''
        <https://tiny-organics.myshopify.com/admin/api/2022-01/customers.json?limit=50&page_info=nextPageData>; 
        rel="next"
    '''
    return response


def _mock_get_request_for_customer(*args, **kwargs):
    return MockedLoggedRequest()


def _mock_get_request_for_customer_paginated(*args, **kwargs):
    return MockedLoggedRequest(paginated=True)


class ShopifyRestClientTestSuite(TestCase):
    def test_can_retrieve_list_of_customers_without_paginated_request(self):
        client = ShopifyRestClient()
        with mock.patch('requests.sessions.Session.get', side_effect=_mock_requests_session_get) as mocked:
            with mock.patch('libs.api_request.make_logged_api_request', side_effect=_mock_get_request_for_customer):
                client.get_customers(CustomerRequestDTO())

        self.assertTrue(mocked.called)

    def test_can_retrieve_list_of_customers_with_paginated_request(self):
        client = ShopifyRestClient()
        with mock.patch('requests.sessions.Session.get', side_effect=_mock_requests_session_get) as mocked:
            with mock.patch('libs.api_request.make_logged_api_request', side_effect=_mock_get_request_for_customer):
                client.get_customers(CustomerRequestDTO(page_info='1'))

        self.assertTrue(mocked.called)

    def test_will_return_none_when_getting_next_page_data_from_previous_requests_and_header_is_not_present(self):
        client = ShopifyRestClient()
        with mock.patch('requests.sessions.Session.get', side_effect=_mock_requests_session_get):
            with mock.patch('libs.api_request.make_logged_api_request', side_effect=_mock_get_request_for_customer):
                response = client.get_customers(CustomerRequestDTO(page_info='1'))

        self.assertIsNone(client.get_next_page_from_response(response))

    def test_will_return_data_when_response_header_contains_link_to_next_page(self):
        client = ShopifyRestClient()
        with mock.patch('requests.sessions.Session.get', side_effect=_mock_requests_session_get_with_headers):
            with mock.patch(
                'libs.api_request.make_logged_api_request',
                side_effect=_mock_get_request_for_customer_paginated
            ):
                response = client.get_customers(CustomerRequestDTO(page_info='1'))

        self.assertIsNotNone(client.get_next_page_from_response(response))
