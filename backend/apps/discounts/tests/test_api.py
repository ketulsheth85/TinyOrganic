import uuid
from contextlib import contextmanager
from unittest import mock

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.carts.tests.factories import CartFactory, CartLineItemFactory
from apps.customers.tests.factories import CustomerChildFactory, CustomerSubscriptionFactory, CustomerFactory
from apps.discounts.libs import CannotCreateDiscountForCustomerError
from apps.discounts.models import CustomerDiscountStatusEnum
from apps.discounts.tests.factories import DiscountFactory, CustomerDiscountFactory


# class DiscountModelTestSuite(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.discount_code = DiscountFactory(
#             banner_text='NEW DISCOUNT :)', is_active=True, is_primary=True)
#
#     def test_will_fetch_active_and_primary_discount_code(self):
#         url = reverse('discount-list')
#         response = self.client.get(url)
#         self.assertIsNotNone(response.json())


class CustomerDiscountTestSuite(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.discount_code = DiscountFactory(
            banner_text='NEW DISCOUNT :)', is_active=True, is_primary=True)
        cls.customer_child = CustomerChildFactory()
        cls.customer_child_subscription = CustomerSubscriptionFactory(
            customer_child=cls.customer_child,
            customer=cls.customer_child.parent,
            is_active=True
        )
        cls.cancellation_discount = DiscountFactory(
            from_brightback=True, is_active=True)

    def setUp(self):
        CartFactory(customer=self.customer_child.parent,
                    customer_child=self.customer_child)

    # def test_will_allow_existing_customer_to_apply_active_discount_code(self):
    #     url = reverse('customerdiscount-list')
    #     response = self.client.post(
    #         url,
    #         data={'customer': self.customer_child.parent.id,
    #               'discount': self.discount_code.codename},
    #     )
    #     self.assertEqual(response.status_code, 200)

    # def test_will_not_allow_customer_to_apply_a_redeemed_discount_code(self):
    #     CustomerDiscountFactory(
    #         customer=self.customer_child.parent,
    #         customer_child=self.customer_child,
    #         status=CustomerDiscountStatusEnum.redeemed,
    #         discount=self.discount_code
    #     )
    #     url = reverse('customerdiscount-list')
    #     response = self.client.post(
    #         url,
    #         data={'customer': self.customer_child.parent.id,
    #               'discount': self.discount_code.codename},
    #     )
    #     self.assertEqual(response.status_code, 403)

    # def test_will_not_allow_customer_to_apply_a_nonexisting_discount_code(self):
    #     url = reverse('customerdiscount-list')
    #     response = self.client.post(
    #         url,
    #         data={'customer': self.customer_child.parent.id,
    #               'discount': 'random-nonexistent-discount'},
    #     )
    #     self.assertEqual(response.status_code, 404)

    def test_allow_customer_to_create_cancellation_discount_with_valid_data(self):
        customer = self.customer_child.parent
        self.client.force_login(customer)
        session = self.client.session
        session_id = str(uuid.uuid4())
        session['brightback_session_id'] = session_id
        session.save()
        url = reverse('customerdiscount-list')
        with mock.patch(
                'apps.discounts.api.viewsets.discount.CustomerDiscountViewSet._assert_valid_cancellation_payload',
                side_effect=lambda *args, **kwargs: None
        ):
            response = self.client.post(url, data={
                'session': session_id,
                'customer': str(customer.id),
                'subscription': str(self.customer_child_subscription.id),
                'discount': str(self.cancellation_discount.codename)
            })
            self.assertEqual(response.json()[0].get(
                'discount'), str(self.cancellation_discount.id))

    def test_customer_without_session_cannot_redeem_cancellation_discount_without_valid_session(self):
        customer = self.customer_child.parent
        url = reverse('customerdiscount-list')

        with self.assertRaises(Exception):
            self.client.post(url, data={
                'customer': str(customer.id),
                'discount': str(self.cancellation_discount.codename)
            })

    def test_customer_cannot_redeem_discount_with_another_customers_session(self):
        customer = self.customer_child.parent
        self.client.force_login(customer)
        session = self.client.session
        session_id = str(uuid.uuid4())
        session['brightback_session_id'] = session_id
        session.save()
        url = reverse('customerdiscount-list')
        customer_without_cancellation_session_child = CustomerChildFactory()
        customer_without_cancellation_session_subscription = CustomerSubscriptionFactory(
            customer=customer_without_cancellation_session_child.parent,
            customer_child=customer_without_cancellation_session_child,
            is_active=True
        )
        CartFactory(
            customer=customer_without_cancellation_session_child.parent,
            customer_child=customer_without_cancellation_session_child
        )
        with self.assertRaises(Exception):
            self.client.post(url, data={
                'session': session_id,
                'customer': str(customer_without_cancellation_session_child.id),
                'subscription': str(customer_without_cancellation_session_subscription),
                'discount': str(self.cancellation_discount.codename)
            })

    def test_customer_cannot_redeem_cancellation_discount_with_the_same_session_twice(self):
        customer = self.customer_child.parent
        self.client.force_login(customer)
        session = self.client.session
        session_id = str(uuid.uuid4())
        session['brightback_session_id'] = session_id
        session.save()
        url = reverse('customerdiscount-list')
        data = {
            'session': session_id,
            'customer': str(customer.id),
            'subscription': str(self.customer_child_subscription.id),
            'discount': str(self.cancellation_discount.codename)
        }

        @contextmanager
        def fake_acquire_shared_lock_context(lock_name, cache_name='default', **kwargs):
            yield lock_name

        with mock.patch(
            'libs.locking.acquire_shared_lock_context',
            side_effect=fake_acquire_shared_lock_context
        ):
            self.client.post(url, data=data)
            with self.assertRaises(CannotCreateDiscountForCustomerError):
                self.client.post(url, data=data)

    def test_customer_cannot_redeem_discount_with_inactive_subscription(self):
        customer_without_cancellation_session_child = CustomerChildFactory()
        self.client.force_login(
            customer_without_cancellation_session_child.parent)
        session_id = uuid.uuid4()
        self.client.session['brightback_session_id'] = session_id
        self.client.session.save()
        customer_without_cancellation_session_subscription = CustomerSubscriptionFactory(
            customer=customer_without_cancellation_session_child.parent,
            customer_child=customer_without_cancellation_session_child,
            is_active=False
        )
        CartFactory(
            customer=customer_without_cancellation_session_child.parent,
            customer_child=customer_without_cancellation_session_child
        )
        url = reverse('customerdiscount-list')
        with self.assertRaises(Exception):
            self.client.post(url, data={
                'session': session_id,
                'customer': str(customer_without_cancellation_session_child.id),
                'subscription': str(customer_without_cancellation_session_subscription),
                'discount': str(self.cancellation_discount.codename)
            })
