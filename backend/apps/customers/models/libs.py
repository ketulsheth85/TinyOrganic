from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class CustomerManager(BaseUserManager):
    """
    Manager class for the custom `Customer` model (auth.USER)
    """
    def create_user(self, email: str, first_name: str, last_name: str, **extra_fields) -> 'Customer':
        """
        Create and save a User with the given email, first name, last name, and password.
        """
        if not email:
            raise ValueError(_('Email is required.'))

        password = None
        if extra_fields.get('password'):
            password = extra_fields.pop('password')

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        user.refresh_from_db()
        return user

    def create_superuser(self, email: str, password: str, first_name: str, last_name: str, **extra_fields) -> 'Customer':
        """
        Create and save a SuperUser with the given email, first name, last name, and password.
        """
        extra_fields = {
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }
        if password:
            extra_fields['password'] = password

        return self.create_user(email, first_name, last_name, **extra_fields)


class PersonMixin:
    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'

