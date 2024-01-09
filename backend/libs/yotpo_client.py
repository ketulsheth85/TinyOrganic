from dataclasses import dataclass
from typing import Union

from libs import api_request
from furl import furl
from settings.minimal import env


class CouldNotCreateYotpoCustomerError(Exception):
    ...


class CouldNotUpdateYotpoCustomerError(Exception):
    ...


class YotpoCustomerDoesNotExistError(Exception):
    ...


class CouldNotGetYotpoCustomerError(Exception):
    ...

class CouldNotCreateYotpoOrderError(Exception):
    ...


class CouldNotCreateYotpoRefundError(Exception):
    ...


@dataclass
class LoyaltyProgramCustomer:
    id: str
    email: str
    first_name: str
    last_name: str


@dataclass
class LoyaltyProgramItem:
    name: str
    price_cents: int
    vendor: str
    id: str
    type: str
    quantity: int
    collections: str

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'price_cents': self.price_cents,
            'vendor': self.vendor,
            'id': self.id,
            'type': self.type,
            'quantity': self.quantity,
            'collections': self.collections
        }


@dataclass
class LoyaltyProgramOrder:
    customer_email: str
    total_amount_cents: int
    currency_code: str
    order_id: str
    status: str
    coupon_code: Union[None, str]
    ignore_ip_ua: bool
    discount_amount_cents: int
    items: list


@dataclass
class LoyaltyProgramRefund:
    order_id: str
    total_amount_cents: int
    currency: str


class YotpoClient:
    base_url = 'https://loyalty.yotpo.com/api/v2'
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-guid": env.str('YOTPO_GUID', default='FAKE'),
        "x-api-key": env.str('YOTPO_API_KEY', default='FAKE')
    }

    def create_customer(self, customer: 'LoyaltyProgramCustomer'):
        url = furl(f'{self.base_url}/customers').url

        logged_api_request_object = api_request.make_logged_api_request(
            url=url,
            method='post',
            headers=self.headers,
            body={
                'email': customer.email,
                'id': str(customer.id),
                'first_name': customer.first_name,
                'last_name': customer.last_name,
            },
            object_type='LoyaltyProgramCustomer',
            object_id=customer.id,
        )

        if logged_api_request_object.response.status_code not in {200, 201}:
            raise CouldNotCreateYotpoCustomerError(
                'Could not create Yotpo customer',
                f'status: {logged_api_request_object.response.status_code}',
                f'body: {logged_api_request_object.response.parsed_body}'
            )
        return logged_api_request_object.response.parsed_body

    def update_customer(self, customer: 'LoyaltyProgramCustomer'):
        url = furl(f'{self.base_url}/customers').url
        logged_api_request_object = api_request.make_logged_api_request(
            url=url,
            method='post',
            headers=self.headers,
            body={
                'email': customer.email,
                'id': str(customer.id),
                'first_name': customer.first_name,
                'last_name': customer.last_name,
            },
            options={'customer_id': customer.id},
            object_type='LoyaltyProgramCustomer',
            object_id=customer.id,
        )
        if logged_api_request_object.response.status_code not in {200, 201}:
            raise CouldNotUpdateYotpoCustomerError(
                'Could not update Yotpo customer',
                f'status: {logged_api_request_object.response.status_code}',
                f'body: {logged_api_request_object.response.parsed_body}'
            )
        return logged_api_request_object.response.parsed_body

    def get_customer(self, customer_id: str):
        url = furl(f'{self.base_url}/customers').url
        logged_api_request_object = api_request.make_logged_api_request(
            url=url,
            method='get',
            options={
                'customer_id': customer_id,
                'with_referral_code': 'true',
                'with_history': 'true',
            },
            headers=self.headers,
            object_type='LoyaltyProgramCustomer',
            object_id=customer_id,
        )
        error_details = {}
        if logged_api_request_object.response.status_code != 200:
            error_details['details'] = 'Yotpo customer does not exist'
            error_details['customer_id'] = f'customer_id: {customer_id}'
            error_details['status'] = logged_api_request_object.response.status_code
            error_details['body'] = logged_api_request_object.response.parsed_body
            raise CouldNotGetYotpoCustomerError(error_details)

        return logged_api_request_object.response.parsed_body

    def create_order(self, order: 'LoyaltyProgramOrder'):
        url = furl(f'{self.base_url}/orders').url
        logged_api_request_object = api_request.make_logged_api_request(
            url=url,
            method='post',
            headers=self.headers,
            body={
                'customer_email': order.customer_email,
                'total_amount_cents': order.total_amount_cents,
                'currency_code': order.currency_code,
                'order_id': order.order_id,
                'status': order.status,
                'coupon_code': order.coupon_code,
                'ignore_ip_ua': order.ignore_ip_ua,
                'discount_amount_cents': order.discount_amount_cents,
                'items': order.items,
            },
            object_type='LoyaltyProgramOrder',
            object_id=order.order_id,
        )

        if logged_api_request_object.response.status_code not in {200, 201}:
            raise CouldNotCreateYotpoOrderError(
                'Could not create Yotpo order',
                f'status: {logged_api_request_object.response.status_code}',
                f'body: {logged_api_request_object.response.parsed_body}'
            )
        return logged_api_request_object.response.parsed_body

    def create_refund(self, refund: 'LoyaltyProgramRefund'):
        url = furl(f'{self.base_url}/refunds').url
        logged_api_request_object = api_request.make_logged_api_request(
            url=url,
            method='post',
            headers=self.headers,
            body={
                'order_id': refund.order_id,
                'total_amount_cents': refund.total_amount_cents,
                'currency': refund.currency,
            },
            object_type='LoyaltyProgramRefund',
            object_id=refund.order_id,
        )

        if logged_api_request_object.response.status_code not in {200, 201}:
            raise CouldNotCreateYotpoRefundError(
                'Could not create Yotpo refund',
                f'status: {logged_api_request_object.response.status_code}',
                f'body: {logged_api_request_object.response.parsed_body}'
            )
        return logged_api_request_object.response.parsed_body
