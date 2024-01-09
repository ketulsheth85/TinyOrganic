from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    ReadOnlyPasswordHashField,
    PasswordResetForm as _PasswordResetForm,
)
from django.utils.translation import ugettext_lazy as _

from apps.customers.models import Customer


class PasswordResetForm(_PasswordResetForm):
    def get_users(self, email):
        return (u for u in Customer.objects.filter(
            is_active=True,
        ))


class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')


class CustomerAddForm(forms.ModelForm):
    first_name = forms.CharField(label='First name')
    last_name = forms.CharField(label='Last name')
    email = forms.EmailField(label='Email')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, required=False)

    class Meta:
        model = Customer
        fields = ('email', 'first_name', 'last_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        customer = super().save(commit=False)
        if not self.cleaned_data['password2'] and not self.cleaned_data['password1']:
            customer.set_unusable_password()
        else:
            customer.set_password(self.cleaned_data['password1'])

        if commit:
            customer.save()
        return customer


class CustomerChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label=_("Password"), help_text=_(
        "Raw passwords are not stored, so there is no way to see "
        "this user's password, but you can change the password "
        "using <a href=\"%(url)s\">this form</a>."
    ) % {'url': '../password/'})

    class Meta:
        model = Customer
        fields = ('first_name', 'last_name', 'email', 'password', 'is_staff', 'is_superuser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial['password']
