from django.test import TestCase

from backend.apps.core.management.commands.seed_initial_data import Command
from apps.customers.models.customer import Customer
from apps.billing.models.payment_processor import PaymentProcessor
from apps.orders.models.shipping_rate import ShippingRate
from apps.discounts.models.discount import Discount
from apps.analytics.models import Pixel

class SeedInitialDataTestSuite(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.seed_initial_data = Command()
        cls.seed_initial_data.handle()

    def test_seeded_user(self):
        # Validate that user is super user
        customer = Customer.objects.get(email='superuser@tinyorganics.com')
        self.assertEqual(customer.is_staff, True)
        self.assertEqual(customer.is_superuser, True)
        self.assertEqual(customer.is_active, True)

    def test_seeded_payment_processor(self):
        # Validate procesor name and is_active flag
        payment_processor = PaymentProcessor.objects.get(name='Stripe')
        self.assertEqual(payment_processor.is_active, True)      

    def test_seeded_shipping_rate(self):
        # Validate shipping rate is_active flag and is_default flag
        shipping_rate = ShippingRate.objects.get(title='Default shipping rate')
        self.assertEqual(shipping_rate.is_active, True)
        self.assertEqual(shipping_rate.is_default, True)

    def test_seeded_discount(self):
        # Validate discount is_active flag and is_primary flag
        discount = Discount.objects.get(codename='Default discount')
        self.assertEqual(discount.is_active, True)
        self.assertEqual(discount.is_primary, True)

    def test_seeded_pixel_record(self):
        # Validate pixel record is_active flag and the tag_script
        pixel = Pixel.objects.get(name='Segment pixel')
        self.assertEqual(pixel.is_active, True)
        self.assertEqual(pixel.tag_script, ('<script>\n' 
                        '!function(){var analytics=window.analytics=window.analytics||[];'
                        'if(!analytics.initialize)if(analytics.invoked)window.console&&console.error&&console.error("Segment snippet included twice.");'
                        'else{analytics.invoked=!0;'
                        'analytics.methods=["trackSubmit","trackClick","trackLink","trackForm","pageview","identify","reset","group","track","ready","alias","debug","page","once","off","on","addSourceMiddleware","addIntegrationMiddleware","setAnonymousId","addDestinationMiddleware"];'
                        'analytics.factory=function(e){return function(){var t=Array.prototype.slice.call(arguments);t.unshift(e);analytics.push(t);'
                        'return analytics}};for(var e=0;e<analytics.methods.length;e++){var key=analytics.methods[e];analytics[key]=analytics.factory(key)}analytics.load=function(key,e){var t=document.createElement("script");'
                        't.type="text/javascript";t.async=!0;t.src="https://cdn.segment.com/analytics.js/v1/" + key + "/analytics.min.js";var n=document.getElementsByTagName("script")[0];'
                        'n.parentNode.insertBefore(t,n);analytics._loadOptions=e};analytics._writeKey="pWWFq4xL2WKhTZxbH0JMKGBF60Io5UaA";;analytics.SNIPPET_VERSION="4.15.3";\n'
                        'analytics.load("pWWFq4xL2WKhTZxbH0JMKGBF60Io5UaA");\n'
                        'analytics.page();\n'
                        '}}();\n'
                        '</script>')
                        )
                        