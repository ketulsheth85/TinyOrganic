from django.apps import apps
from django.conf import settings

from libs.api_request import make_logged_api_request
from settings.minimal import env
from furl import furl


class CannotCreateBrightBackSessionURL(Exception):
    ...


class BrightBackClient:

    def __init__(self, subscription: 'Subscription', session_id: 'string'):
        self.customer = subscription.customer
        self.subscription = subscription
        self.session_id = session_id
        self.bright_back_app_id = settings.BRIGHTBACK_APP_ID
        self.bright_back_base_url = "https://app.brightback.com"
        self.cancellation_payload = {
            "app_id": self.bright_back_app_id,
            "subscription_id": str(self.subscription.id),
            "email": self.customer.email,
            "account": {
                "internal_id": str(self.customer.id)
            },
            "save_return_url": f"{self._get_base_url()}/dashboard/",
            "cancel_confirmation_url":
                f"{self._get_base_url()}/dashboard/subscription_cancellation?subscription={self.subscription.id}",
            "custom": self._get_cancellation_discount_urls()
        }

    def _get_base_url(self):
        # Add protocol to url
        return f'https://{settings.BRIGHTBACK_BASE_REDIRECT_URL}'

    def _get_cancellation_discount_urls(self):
        Discount = apps.get_model('discounts', 'Discount')
        cancellation_discounts = Discount.objects.filter(
            is_active=True,
            from_brightback=True
        )

        cancellation_discount_dict = {}

        for discount in cancellation_discounts:
            cancellation_discount_dict[discount.codename] = \
                furl(f'{self._get_base_url()}/dashboard/cancellation_redemption') \
                .add(
                {
                    'session': self.session_id,
                    'subscription': self.subscription.id,
                    'coupon_code': discount.codename,
                }
            ).url

        return cancellation_discount_dict

    def get_cancellation_url(self):
        response = make_logged_api_request(
            url=f'{self.bright_back_base_url}/precancel',
            method='post',
            body=self.cancellation_payload
        )

        response = response.response

        if not response.parsed_body.get('valid'):
            raise CannotCreateBrightBackSessionURL(
                f'Customer: {self.customer}, Subscription: {self.subscription}, Error: {response.body.get("message")}'
            )

        return response.parsed_body.get("url")
