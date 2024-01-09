from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import MultipleObjectsReturned


class CaseInsensitiveModelBackend(ModelBackend):
    def _get_user(self, username, password, **kwargs):
        from django.apps import apps
        Customer = apps.get_model('customers', 'Customer')

        try:
            user = Customer.objects.get(email__iexact=username)
            return user
        except Customer.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            Customer().set_password(password)
        except MultipleObjectsReturned:
            user = Customer.objects.filter(
                subscriptions__is_active=True,
                email__iexact=username,
            ).order_by('-created_at').first()
            if not user:
                user = Customer.objects.filter(email__iexact=username).order_by('-created_at').first()
            return user

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = self._get_user(username, password, **kwargs)
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
