import uuid
from dataclasses import dataclass
from typing import Union
from urllib import parse

import requests

from apps.core.exceptions import APIRateLimitError
from libs.api_request import make_logged_api_request, APIResponseDTO
from settings.minimal import env


@dataclass
class CustomerRequestDTO:
    page_info: Union[str, None] = None
    start_date: Union[str, None] = None
    end_date: Union[str, None] = None


class ShopifyRestClient:
    def __init__(self, *args, **kwargs):
        self.SHOPIFY_API_KEY = env.str('SHOPIFY_API_KEY', default='FAKE')
        self.SHOPIFY_API_SECRET_KEY = env.str('SHOPIFY_API_KEY_SECRET', default='FAKE')
        self.SHOPIFY_DOMAIN = env.str('SHOPIFY_DOMAIN', default='FAKE')
        self.SHOPIFY_PASSWORD = env.str('SHOPIFY_PASSWORD', default='FAKE')
        self.BASE_URI = f'https://{self.SHOPIFY_API_KEY}:{self.SHOPIFY_PASSWORD}@{self.SHOPIFY_DOMAIN}'
        self.session = requests.Session()

    def get_customers(self, request_params: CustomerRequestDTO) -> APIResponseDTO:
        url = f'{self.BASE_URI}/admin/api/2022-01/customers.json'
        options = {
            'limit': 250,
            'fields': 'id,email,first_name,last_name,phone,orders_count,addresses',
        }
        if request_params.page_info:
            options['page_info'] = request_params.page_info

        if request_params.start_date:
            options['created_at_min'] = request_params.start_date

        logged_request = make_logged_api_request(url=url, headers={}, options=options, object_type='Customer')
        return logged_request.response

    def _sanitize_next_link_info(self, next_link_info: str) -> str:
        return next_link_info.replace('<', '').replace('>', '')

    def _extract_next_page_info_from_link_info(self, next_link_info: str) -> str:
        links = next_link_info.replace('<', '').replace('>', '').split(';')
        if ' rel="next"' in links:
            return dict(parse.parse_qsl(parse.urlsplit(links[-2]).query))['page_info']
        return ''

    def get_next_page_from_response(self, response: APIResponseDTO) -> Union[str, None]:
        if response.headers.get('Link'):
            next_link_info = self._sanitize_next_link_info(response.headers.get('Link'))
            return self._extract_next_page_info_from_link_info(next_link_info)
        return None

    def get_metafields_for_object(self, obj_name, obj_id):
        url = f'{self.BASE_URI}/admin/{obj_name}/{obj_id}/metafields.json'
        logged_request = make_logged_api_request(url=url, headers={}, options={}, object_type='Customer')
        if logged_request.response.status_code == 429:
            raise APIRateLimitError
        return logged_request.response

    def get_products(self):
        url = f'{self.BASE_URI}/admin/products.json'
        print("=============>>>",url)
        return make_logged_api_request(
            url=url,
            headers={},
            options={'limit': '250'},
            object_type='Product',
            object_id=f'{uuid.uuid4()}',
        ).response.parsed_body['products']

    def get_customer_with_shopify_customer_id(
        self,
        shopify_customer_id: str
    ):
        url = f'{self.BASE_URI}/admin/api/2022-01/customers/{shopify_customer_id}.json'
        return make_logged_api_request(
            url=url,
            object_type='ShopifyCustomer',
            object_id=f'{uuid.uuid4()}',
        )

    def get_order_with_shopify_order_id(
        self,
        shopify_order_id: str,
    ):
        url = f'{self.BASE_URI}/admin/api/2022-01/orders/{shopify_order_id}.json'
        return make_logged_api_request(
            url=url,
            object_type='ShopifyCustomer',
            object_id=f'{uuid.uuid4()}',
        )
