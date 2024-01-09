from apps.orders.tasks.notifications import (
    sync_order_placed_event,
    sync_order_payment_failed_to_analytics,
    send_order_confirmation_email,
)
from apps.orders.tasks.order import (
    sync_order_to_shopify,
    sync_refunded_order_to_shopify,
    sync_order_to_tax_client,
    sync_refund_to_tax_client,
    sync_partial_refund_to_shopify,
)
from apps.orders.tasks.recurring import (
    sync_unsynced_orders_to_shopify,
    create_new_orders_for_active_subscribers,
    sync_unsynced_orders_to_shopify,
    delete_pending_orders_for_non_subscribers,
    sync_unsynced_orders_to_tax_client,
)
from apps.orders.tasks.loyalty import (
    sync_order_to_yotpo,
    sync_refund_to_yotpo,
)

from django.template.loader import render_to_string
