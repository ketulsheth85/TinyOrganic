from django.test import TestCase

from apps.customers.tests.factories import CustomerFactory, CustomerChildFactory, CustomerSubscriptionFactory


class CaseInsensitiveBackendTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.customer_with_mixed_case = CustomerFactory(email='MyMiXeDcAsE@EmAIL.com', is_active=True)
        cls.password = 'some-password!'
        cls.customer_with_mixed_case.set_password(cls.password)
        cls.customer_with_mixed_case.save()

        cls.customer_with_duplicate_email_and_subscription1 = CustomerFactory(email='dUpLiCaTe@gmail.com')
        cls.customer_with_duplicate_email_and_subscription1.set_password(cls.password)
        cls.customer_with_duplicate_email_and_subscription1.save()
        cls.customer_with_duplicate_email_and_subscription2 = CustomerFactory(email='duplicate@gmail.com')
        cls.customer_with_duplicate_email_and_subscription2.set_password(cls.password)
        cls.customer_with_duplicate_email_and_subscription2.save()

        child1 = CustomerChildFactory(parent=cls.customer_with_duplicate_email_and_subscription1)
        child2 = CustomerChildFactory(parent=cls.customer_with_duplicate_email_and_subscription2)
        CustomerSubscriptionFactory(
            is_active=True,
            status='active',
            customer_child=child1,
        )
        CustomerSubscriptionFactory(
            is_active=False,
            status='inactive',
            customer_child=child2
        )

    def test_can_login_with_mixed_letter_cased_email_address(self):
        response = self.client.login(username=self.customer_with_mixed_case.email, password=self.password)
        self.assertTrue(response)

    def test_cannot_login_with_incorrect_email_address(self):
        response = self.client.login(username='wrong@gmail.com', password=self.password)
        self.assertFalse(response)

    def test_can_login_if_customer_has_more_than_one_subscription(self):
        response = self.client.login(
            username=self.customer_with_duplicate_email_and_subscription1.email,
            password=self.password,
        )
        self.assertTrue(response)
