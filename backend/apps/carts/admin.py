from django.contrib import admin
from django.contrib.admin import register
from simple_history.admin import SimpleHistoryAdmin

from apps.carts.models import Cart, CartLineItem


class CartLineItemInline(admin.TabularInline):
    model = CartLineItem
    readonly_fields = 'id',
    extra = 0
    verbose_name = 'Line Item'
    verbose_name_plural = 'Line Items'
    raw_id_fields = 'cart',


@register(Cart)
class CartAdmin(SimpleHistoryAdmin):
    search_fields = 'customer__email', 'id',
    list_display = 'id', 'customer',
    inlines = CartLineItemInline,
    readonly_fields = 'id',
    ordering = '-created_at',
    raw_id_fields = 'customer', 'customer_child',
