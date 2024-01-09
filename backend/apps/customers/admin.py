from django.contrib import admin
from django.contrib.admin import register
from django.urls import path
from fsm_admin.mixins import FSMTransitionMixin
from hijack.contrib.admin import HijackUserAdminMixin
from simple_history.admin import SimpleHistoryAdmin

from apps.addresses.models import Location
from apps.core.admin import CoreAdmin
from apps.customers.forms import CustomerAddForm, CustomerChangeForm
from apps.customers.models import Customer, CustomerChild, CustomerSubscription
from apps.customers.views import (
    SyncUnsyncedOrdersToShopify,
)


class CustomerChildAdminInline(admin.TabularInline):
    model = CustomerChild
    readonly_fields = 'id',
    extra = 1
    raw_id_fields = 'parent',


class CustomerSubscriptionAdminInline(admin.TabularInline):
    model = CustomerSubscription
    readonly_fields = 'id', 'activated_at', 'deactivated_at', 'paused_at',
    extra = 0
    raw_id_fields = 'customer', 'customer_child',


class CustomerAddressAdminInline(admin.TabularInline):
    model = Location
    extra = 0
    verbose_name_plural = 'Addresses'
    raw_id_fields = 'customer',


class CustomHijackUserAdminMixin(HijackUserAdminMixin):
    hijack_success_url = '/'


@register(Customer)
class CustomerAdmin(CustomHijackUserAdminMixin, SimpleHistoryAdmin):
    add_form = CustomerAddForm
    form = CustomerChangeForm
    fieldsets = (
        (None, {
            'fields': (
                'first_name',
                'last_name',
                'email',
                'payment_provider_customer_id',
                'password',
            ),
        }),
        ('More Data', {
            'fields': (
                'has_active_subscriptions',
                'phone_number',
                'guardian_type',
            )
        }),
        ('Shopify', {
            'fields': (
                'external_customer_id',
            )
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'is_active',),
        }),
    )
    list_display = (
        'email',
        'is_active',
        'is_staff',
        'is_superuser',
        'has_active_subscriptions',
        'status',
        'external_customer_id',
        'recharge_customer_id',
        'created_at',
        'modified_at',
    )
    history_list_display = 'email', 'is_active', 'status'
    search_fields = 'email', 'first_name', 'last_name', 'id'
    ordering = 'email',
    readonly_fields = 'password', 'external_customer_id', 'recharge_customer_id', 'payment_provider_customer_id',
    inlines = CustomerChildAdminInline, CustomerSubscriptionAdminInline, CustomerAddressAdminInline,


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'sync-unsync-order-to-shopify/',
                self.admin_site.admin_view(SyncUnsyncedOrdersToShopify.as_view()),
                name='sync-orders-to-shopify',
            )
          ] + urls
        return custom_urls


@register(CustomerChild)
class CustomerChildAdmin(admin.ModelAdmin):
    readonly_fields = 'id',
    raw_id_fields = 'parent',
    search_fields = 'id', 'parent__email',
    list_display = 'id', 'parent', 'birth_date', 'sex',

    def get_queryset(self, request):
        return CustomerChild.objects.filter(is_deleted=False).order_by('parent__email')


@register(CustomerSubscription)
class CustomerSubscriptionAdmin(FSMTransitionMixin, CoreAdmin):
    readonly_fields = 'id', 'activated_at', 'deactivated_at', 'paused_at',
    fsm_field = ['status', ]
    ordering = ['-created_at', ]
    list_display = (
        'id',
        'customer',
        'is_active',
        'status',
        'frequency',
        'number_of_servings',
        'next_order_charge_date',
        'activated_at',
        'paused_at',
        'deactivated_at',
        'created_at',
    )
    raw_id_fields = 'customer_child', 'customer'
    search_fields = 'id', 'customer__email',

    def get_queryset(self, request):
        return CustomerSubscription.objects.filter().prefetch_related('customer', 'customer_child')
