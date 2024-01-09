import os

from django.test import SimpleTestCase

from libs.email import _scrub_email_address


class EmailLibsTestSuite(SimpleTestCase):
    def test_will_not_send_email_message_when_recipient_does_not_have_tinyorganics_email_address(self):
        self.assertNotEqual(_scrub_email_address('customer@gmail.com'), 'customer@gmail.com')

    def test_will_send_email_message_when_environment_in_production(self):
        os.environ['ENVIRONMENT'] = 'production'
        self.assertEqual(_scrub_email_address('customer@gmail.com'), 'customer@gmail.com')

    def test_will_return_tinyorganics_email_address(self):
        self.assertEqual(_scrub_email_address('raul+test@tinyorganics.com'), 'raul@tinyorganics.com')
