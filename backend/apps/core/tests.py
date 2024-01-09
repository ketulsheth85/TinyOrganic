from contextlib import nullcontext
from django.http import response
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from apps.core.templatetags.settings import setting

from django.contrib.auth import get_user_model

class SettingTemplateTagTestSuite(SimpleTestCase):
    def test_will_return_setting_if_it_exists(self):
        self.assertIsNotNone(setting('DEBUG'))

    def test_will_return_setting_if_setting_is_dict(self):
        self.assertIsNotNone(setting('CACHES'), 'default')

class RobotsTXTTestSuite(TestCase):
    def test_can_access_page(self):
        response = self.client.get(reverse('robots_rule_list'))
        self.assertEqual(response.status_code, 200)

        