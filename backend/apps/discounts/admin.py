from django.contrib import admin
from django.contrib.admin import register
from apps.core.admin import CoreAdmin
from apps.discounts.models import Discount, Rule, CustomerDiscount


class DiscountRuleAdminInline(admin.TabularInline):
    filter_horizontal = 'apply_to_customers', 'apply_to_products',
    model = Rule
    extra = 0
    raw_id_fields = 'discount', 'apply_to_customers', 'apply_to_products',


@register(Discount)
class DiscountAdmin(CoreAdmin):
    list_display = 'id', 'codename', 'referrer', 'discount_type', 'amount', 'is_active', 'is_primary', \
                   'deactivate_at', 'created_at', 'from_yotpo',
    inlines = DiscountRuleAdminInline,
    search_fields = 'id', 'codename',

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)

        return readonly_fields + (
            'redemption_count',
            'activated_at',
            'deactivated_at',
            'from_yotpo'
        )


@register(CustomerDiscount)
class CustomerDiscountAdmin(CoreAdmin):
    search_fields = 'id', 'customer__email', 'discount__codename',
    raw_id_fields = 'customer', 'discount', 'customer_child',
    list_display = (
        'id',
        'customer',
        'discount',
        'is_active',
        'redeemed_at',
        'applied_at',
        'created_at',
    )
