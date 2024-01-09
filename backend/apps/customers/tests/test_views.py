from django.test import SimpleTestCase
from rest_framework.reverse import reverse


class LoginViewTestCase(SimpleTestCase):
    def can_render_page_login_view(self):
        url = reverse('login')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


class ResetPasswordViewTestCase(SimpleTestCase):
    def can_render_page_login_view(self):
        url = reverse('password_reset')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


class ResetPasswordDoneViewTestCase(SimpleTestCase):
    def can_render_page_login_view(self):
        url = reverse('password_reset_done')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


class ResetPasswordDoneView(SimpleTestCase):
    def can_render_page_login_view(self):
        url = reverse('password_reset_confirm')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


class ResetPasswordDoneViewTestCase(SimpleTestCase):
    def can_render_page_login_view(self):
        url = reverse('password_reset_complete')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
