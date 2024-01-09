from unittest.mock import patch

from django.test import SimpleTestCase
from requests import Session

from libs.api_request import (
    APIResponseDTO,
    APIRequestDTO,
    make_api_request,
)


class MockResponse:
    def __init__(self):
        self.status_code = 204
        self.headers = {'eat': 'yes please'}
        self.content = "{\"meat\": \"chorizo\"}"


class APIRequestTestSuite(SimpleTestCase):
    @patch.object(Session, 'get', return_value=MockResponse())
    def setUp(self, cls):
        self.api_request = make_api_request(
            url='http://tacos.are.awesome',
            options={'tasty': True},
            method='get',
        )

    def test_returns_an_api_response_object_from_request(self):
        self.assertIsInstance(
            self.api_request,
            APIRequestDTO,
        )

    def test_returned_api_request_matches_url_and_headers(self):
        self.assertEqual(
            self.api_request.url,
            'http://tacos.are.awesome?tasty=True',
        )

    def test_returned_api_response_has_parsed_body_from_json(self):
        self.assertEqual(
            self.api_request.response.parsed_body,
            {'meat': 'chorizo'},
        )


class APIResponseDTOTestSuite(SimpleTestCase):
    def test_api_request_dto_raises_error_when_http_method_invalid(self):
        with self.assertRaises(AssertionError):
            APIResponseDTO(
                status_code=9000,
                headers={},
                raw_body={},
                parsed_body={}
            )
