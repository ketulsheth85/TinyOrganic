import datetime
from unittest import mock

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from apps.carts.tests.factories import CartFactory
from apps.customers.tests.factories.customer import CustomerFactory
from apps.customers.tests.factories.customer_child import CustomerChildFactory
from apps.customers.tests.factories.customer_subscription import CustomerSubscriptionFactory
from apps.discounts.tests.factories import DiscountFactory
from apps.products.tests.factories import ProductFactory, ProductVariantFactory
from apps.recipes.tests.factories import IngredientFactory
from libs.brightback_client import CannotCreateBrightBackSessionURL


class CustomerViewSetTestCase(APITestCase):
    def test_responds_with_201_status_code_when_creating_new_customer(self):
        customer_data = CustomerFactory.build()
        url = reverse('customer-list')
        response = self.client.post(url, data={
            'email': customer_data.email,
            'firstName': customer_data.first_name,
            'lastName': customer_data.last_name,
        }
        )
        self.assertEquals(response.status_code, 201)

    def test_responds_with_200_status_code_when_creating_and_customer_already_exists(self):
        customer = CustomerFactory(status='lead')
        url = reverse('customer-list')
        response = self.client.post(url, data={
            'email': customer.email,
            'firstName': customer.first_name,
            'lastName': customer.last_name,
        })

        self.assertEquals(response.status_code, 200)

    def test_can_view_children_information_in_json_response_payload(self):
        customer = CustomerFactory()
        child = CustomerChildFactory(parent=customer)

        url = reverse('customer-detail', args=[str(customer.id)])
        response = self.client.get(url)
        self.assertDictContainsSubset(
            response.json()['children'][0],
            {
                'id': str(child.id),
                'parent': str(customer.id),
                'sex': child.sex,
                'birthDate': str(child.birth_date),
                'firstName': child.first_name,
                'allergies': list(child.allergies.filter()),
                'allergySeverity': child.allergy_severity,
            }
        )

    def test_can_view_subscription_information_in_json_response_payload(self):
        customer = CustomerFactory()
        child = CustomerChildFactory(parent=customer)
        subscription = CustomerSubscriptionFactory(
            customer=customer, customer_child=child)

        url = reverse('customer-detail', args=[str(customer.id)])
        response = self.client.get(url)

        subscription_response = response.json()['subscriptions'][0]
        del subscription_response['createdAt']
        del subscription_response['modifiedAt']

        self.assertIsNotNone(subscription_response)

    def test_can_update_charge_date_for_subscription(self):
        customer = CustomerFactory()
        child = CustomerChildFactory(parent=customer)
        subscription = CustomerSubscriptionFactory(
            customer=customer, customer_child=child)
        url = reverse('customersubscription-detail', args=[subscription.id])
        new_charge_date = datetime.datetime.now() + datetime.timedelta(1)

        response = self.client.patch(url, {
            'subscription': subscription.id, 'nextOrderChargeDate': new_charge_date.strftime("%Y-%m-%d")
        })
        data = response.json()
        self.assertEquals(data.get('nextOrderChargeDate'),
                          new_charge_date.strftime("%Y-%m-%d"))

    def test_can_change_password_after_password_is_set(self):
        customer = CustomerFactory()
        customer_url = reverse('customer-detail', args=[str(customer.id)])

        password_set_url = reverse(
            'customer-set-password', args=[str(customer.id)])
        self.client.post(password_set_url, {
            'password': 'very-secure-password'
        })

        response = self.client.get(customer_url)
        api_customer = response.json()

        # verify user has_password is Truthy
        self.assertEquals(api_customer.get('hasPassword'), True)


class CustomerChildViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.parent = CustomerFactory()

    def test_can_create_one_child_for_parent(self):
        customer_child_data = CustomerChildFactory.build(parent=self.parent)
        url = reverse('customerchild-list')
        response = self.client.post(url, data={
            'parent': str(self.parent.id),
            'firstName': customer_child_data.first_name,
            'sex': 'male',
            'birthDate': customer_child_data.birth_date,
        })
        self.assertEquals(response.status_code, 201)

    def test_can_update_existing_child(self):
        customer_child = CustomerChildFactory(parent=self.parent)
        url = reverse('customerchild-detail', args=[str(customer_child.id)])
        response = self.client.patch(url, data={
            'firstName': 'Stewie'
        })
        self.assertEquals(response.json()['firstName'], 'Stewie')

    def test_can_delete_existing_child(self):
        customer_child = CustomerChildFactory(parent=self.parent)
        url = reverse('customerchild-detail', args=[str(customer_child.id)])
        response = self.client.delete(url)
        self.assertEquals(response.status_code, 204)

    def test_can_add_allergies_with_ingredient_id(self):
        ingredient = IngredientFactory(name='Cinnamon')
        customer_child = CustomerChildFactory(parent=self.parent)
        url = reverse('customerchild-detail', args=[str(customer_child.id)])
        response = self.client.patch(
            url, {'allergies': [str(ingredient.id), ]})
        self.assertEqual([str(ingredient.id)], [allergy['id']
                         for allergy in response.json()['allergies']])

    def test_will_not_display_recipes_containing_child_allergens(self):
        ingredient = IngredientFactory(name='Cinnamon')
        ProductFactory(title='Cinnabun', ingredients=[ingredient, ])
        customer_child = CustomerChildFactory(
            parent=self.parent, allergies=[ingredient, ])
        CartFactory(customer=customer_child.parent,
                    customer_child=customer_child)
        url = reverse('customerchild-recommended-products',
                      args=[str(customer_child.id)])
        response = self.client.get(url)
        self.assertEquals(response.json()['recommendations'], [])

    def test_will_display_product_data_in_meal_plan_recommendations(self):
        ingredient = IngredientFactory(name='Cinnamon')
        ProductFactory(title='Cinnabun', ingredients=[ingredient, ])
        customer_child = CustomerChildFactory(parent=self.parent,)
        CartFactory(customer=customer_child.parent,
                    customer_child=customer_child)
        url = reverse('customerchild-recommended-products',
                      args=[str(customer_child.id)])
        response = self.client.get(url)
        self.assertIsNotNone(response.json()['recommendations'][0]['product'])


class CustomerSubscriptionViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.parent = CustomerFactory()
        cls.products = [
            ProductFactory(title=f'recipe-1'),
            ProductFactory(title=f'recipe-2'),
        ]
        for product in cls.products:
            ProductVariantFactory(product=product, sku_id='SKU-12')
            ProductVariantFactory(product=product, sku_id='SKU-24')

    def test_response_with_201_status_code_when_creating_new_subscription(self):
        child = CustomerChildFactory(parent=self.parent)
        url = reverse('customersubscription-list')
        response = self.client.post(url, data={
            'customer': self.parent.id,
            'customerChild': child.id,
            'frequency': 12,
            'numberOfServings': 24,
        })

        self.assertEquals(response.status_code, 201)

    def test_response_with_200_status_code_when_creating_a_subscription_that_exists(self):
        with self.captureOnCommitCallbacks(execute=True):
            child = CustomerChildFactory(parent=self.parent)
        CustomerSubscriptionFactory(
            customer=self.parent,
            customer_child=child,
            frequency=2,
            number_of_servings=12
        )
        url = reverse('customersubscription-list')
        response = self.client.post(url, data={
            'customer': self.parent.id,
            'customerChild': child.id,
            'frequency': 12,
            'numberOfServings': 24,
        })
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json()['numberOfServings'], 24)

    def test_can_cancel_subscription(self):
        with self.captureOnCommitCallbacks(execute=True):
            child = CustomerChildFactory(parent=self.parent)
        subscription = CustomerSubscriptionFactory(
            customer=self.parent,
            customer_child=child,
            frequency=2,
            number_of_servings=12,
            status='active'
        )

        url = reverse('customersubscription-cancel',
                      args=[f'{subscription.id}'])
        response = self.client.put(url, {}, format='json')
        self.assertEquals(response.json()['status'], 'inactive')

    def test_can_reactivate_subscription(self):
        with self.captureOnCommitCallbacks(execute=True):
            child = CustomerChildFactory(parent=self.parent)
        subscription = CustomerSubscriptionFactory(
            customer=self.parent,
            customer_child=child,
            frequency=2,
            number_of_servings=12,
            status='active'
        )

        url = reverse('customersubscription-cancel',
                      args=[f'{subscription.id}'])
        response = self.client.put(url, {}, format='json')
        self.assertEquals(response.json()['status'], 'inactive')

        url = reverse('customersubscription-reactivate',
                      args=[f'{subscription.id}'])

        with mock.patch(
            'apps.customers.models.customer_subscription.CustomerSubscription._create_order',
            side_effect=lambda: True,
        ):
            response = self.client.put(url, {}, format='json')

        self.assertEquals(response.json()['status'], 'active')

    def test_attempts_to_create_order_when_reactivating_subscription(self):
        with self.captureOnCommitCallbacks(execute=True):
            child = CustomerChildFactory(parent=self.parent)
        subscription = CustomerSubscriptionFactory(
            customer=self.parent,
            customer_child=child,
            frequency=2,
            number_of_servings=12,
            status='active'
        )

        url = reverse('customersubscription-cancel',
                      args=[f'{subscription.id}'])
        response = self.client.put(url, {}, format='json')
        self.assertEquals(response.json()['status'], 'inactive')

        url = reverse('customersubscription-reactivate',
                      args=[f'{subscription.id}'])

        with mock.patch(
            'apps.customers.models.customer_subscription.CustomerSubscription._create_order',
            side_effect=lambda: True,
        ) as mocked:
            self.client.put(url, {}, format='json')
        self.assertTrue(mocked.called)

    def cannot_update_charge_date_to_invalid_date(self):
        customer = CustomerFactory()
        child = CustomerChildFactory(parent=customer)
        subscription = CustomerSubscriptionFactory(
            customer=customer, customer_child=child)
        url = reverse('customersubscription-detail', args=[subscription.id])
        new_charge_date = datetime.datetime.now() + datetime.timedelta(days=84)

        response = self.client.patch(url, {
            'nextOrderChargeDate': new_charge_date.strftime('%Y-%m-%d'),
        })
        self.assertEquals(response.status_code, 400)

    def test_can_get_cancel_url_for_customer(self):
        subscription = CustomerSubscriptionFactory(is_active=True)
        url = reverse('customersubscription-precancel', args=[subscription.id])
        mock_bright_back_url = 'http://url.com'
        DiscountFactory(
            codename='25_discount',
            is_active=True,
            from_brightback=True
        )
        with mock.patch(
                'libs.brightback_client.BrightBackClient.get_cancellation_url',
                side_effect=lambda *args, **kwargs: mock_bright_back_url
        ):
            response = self.client.get(url)
            self.assertEquals(response.json().get('url'), mock_bright_back_url)

    def test_will_send_back_error_brightback_fails_to_cancel(self):
        subscription = CustomerSubscriptionFactory(is_active=True)
        url = reverse('customersubscription-precancel', args=[subscription.id])

        with mock.patch(
                'libs.brightback_client.BrightBackClient.get_cancellation_url',
                side_effect=[CannotCreateBrightBackSessionURL(
                    "There's been an error")]
        ):
            response = self.client.get(url)
            self.assertEquals(400, response.status_code)
