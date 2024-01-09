from django.core.management.base import BaseCommand
from apps.customers.models.customer import Customer
from apps.billing.models.payment_processor import PaymentProcessor
from apps.orders.models.shipping_rate import ShippingRate
from apps.discounts.models.discount import Discount
from apps.analytics.models import Pixel

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding minimum data required for development...')

        # Create superuser
        customer = Customer.objects.create_superuser(
            email='superuser@tinyorganics.com',
            password='tinythoughtproperty1',
            first_name='super',
            last_name='user'
        )

        # Because our implementation of the customer object sets an 
        # unusuable_password on create (to support sessions without passwords), 
        # we override that behavior here by creating the password again. 
        customer.set_password('tinythoughtproperty1')
        customer.save()

        # Create Payment Processor
        PaymentProcessor.objects.create(
            name = 'Stripe',
            is_active = True
        )

        # Create Shipping Rate
        ShippingRate.objects.create(
            title = 'Default shipping rate',
            price = 5.99,
            is_active = True,
            is_default = True,
        )

        # Create Discount
        Discount.objects.create(
            codename = 'Default discount',
            discount_type = 'fixed amount',
            amount = 30.00,
            is_active = True,
            is_primary = True,
        )

        # Create Pixel record
        Pixel.objects.create(
            name = 'Segment pixel',
            is_active = True,
            tag_script = ('<script>\n' 
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
