"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, re_path, reverse
from django.urls.conf import include
from django.views.generic import TemplateView, RedirectView

from apps import urls as app_urls
from apps.billing.views import ImportRefundView
from apps.core.views import DashboardView, OnboardingView
from apps.customers.views import (
    LoginView,
    ResetPasswordCompleteView,
    ResetPasswordConfirmView,
    ResetPasswordDoneView,
    ResetPasswordView,
    UpdateSubscriptionNextOrderChargeDateCSVView,
    SendCustomerConfirmationEmails,
)
from apps.discounts.views import ImportDiscountCodesView
from apps.fulfillment.views import UploadFulfillmentCenterZipcodes
from apps.orders.views import UploadShopifyOrdersCSVView


class RedirectCustomerView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        customer = self.request.user
        if (
            customer and customer.is_authenticated and customer.has_active_subscriptions) or (
            customer and customer.is_staff
        ):
            return '/dashboard/'
        return reverse('login')


urlpatterns = [
    path('hijack/', include('hijack.urls')),
    re_path(r'admin/?', admin.site.urls),
    path('accounts/password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('accounts/password-reset-done/', ResetPasswordDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', ResetPasswordConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', ResetPasswordCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path(r'health-check/', include('health_check.urls')),
    path('grappelli/', include('grappelli.urls')),  # grappelli URLS
    re_path(
        r'^admin/billing/paymentoption/stripe_token/',
        TemplateView.as_view(template_name='admin/billing/paymentoption.stripe.html'),
        name='stripe_admin_add_payment_option'
    ),
    path(
        'upload-discount-codes-csv/',
        ImportDiscountCodesView.as_view(),
        name='upload_discount_codes',
    ),
    path(
        'update-subscription-charge-dates-csv/',
        UpdateSubscriptionNextOrderChargeDateCSVView.as_view(),
        name='update-next-order-charge-dates-csv',
    ),
    path(
        'send-confirmation-email-csv/',
        SendCustomerConfirmationEmails.as_view(),
        name='send-confirmation-email-from-csv',
    ),
    path(
        'upload-fufillment-center-zipcodes-csv/',
        UploadFulfillmentCenterZipcodes.as_view(),
        name='upload-fulfillment-center-zipcodes-csv',
    ),
    path('upload-shopify-csv/', UploadShopifyOrdersCSVView.as_view(), name='upload-order-csv'),
    path('upload-refund-csv/', ImportRefundView.as_view(), name='bulk_upload_refunds'),
    path('api/v1/', include(app_urls)),
    path('api-auth/', include('rest_framework.urls')),
    re_path(r'dashboard/*', DashboardView.as_view()),
    re_path(r'onboarding/*', OnboardingView.as_view()),
    re_path(r'post-purchase/*', include('apps.core.urls')),
    re_path(r'^robots\.txt', include('robots.urls')),

    re_path(r'', RedirectCustomerView.as_view()),  # include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
