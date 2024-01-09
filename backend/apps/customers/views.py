from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from django.urls import reverse

from apps.core.views import CoreUploadCSVView
from apps.customers.forms import CustomerLoginForm, PasswordResetForm
from apps.customers.tasks import (
    create_customers_from_file,
    create_subscriptions_from_file,
    update_next_order_charge_dates_from_file,
)
from apps.customers.tasks.imports import send_confirmation_email_from_file


class LoginView(auth_views.LoginView):
    form_class = CustomerLoginForm
    template_name = 'login.html'


class ResetPasswordView(PasswordResetView, PasswordResetForm):
    template_name = 'reset-password.html'
    email_template_name = 'reset-password-email.html'
    subject_template_name = 'password-reset-subject.txt'


class ResetPasswordConfirmView(PasswordResetConfirmView):
    template_name = 'password-reset-confirm.html'


class ResetPasswordDoneView(PasswordResetDoneView):
    template_name = 'reset-password-done.html'
    title = 'Success'


class ResetPasswordCompleteView(PasswordResetCompleteView):
    template_name = 'password-reset-complete.html'
    title = 'Password Reset Complete'


class SyncUnsyncedOrdersToShopify(View):
    @method_decorator(staff_member_required)
    def get(self, request, *args, **kwargs):
        from apps.orders.tasks import sync_unsynced_orders_to_shopify
        sync_unsynced_orders_to_shopify.delay()
        return redirect('admin:customers_customer_changelist')


@method_decorator(staff_member_required, name='dispatch')
class UpdateSubscriptionNextOrderChargeDateCSVView(CoreUploadCSVView):
    template_name = 'uploads/next-order-subscription-dates.html'
    async_function = update_next_order_charge_dates_from_file
    view_name = 'update-next-order-charge-dates-csv'


@method_decorator(staff_member_required, name='dispatch')
class SendCustomerConfirmationEmails(CoreUploadCSVView):
    template_name = 'uploads/send-confirmation-email.html'
    async_function = send_confirmation_email_from_file
    view_name = 'send-confirmation-email-from-csv'
    
    