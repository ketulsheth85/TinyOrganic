from decimal import Decimal
from sys import implementation

import analytics
from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.template import loader

from apps.core.tasks import HttpErrorRetryTask
from libs.email import send_email_message, _scrub_email_address
from libs.tax_nexus.avalara import TaxProcessorClient


@shared_task(base=HttpErrorRetryTask)
def sync_order_placed_event(order_id: str):
    Order = apps.get_model('orders', 'Order')
    order = Order.objects.get(id=order_id)
    customer = order.customer
    if not settings.DEBUG or not settings.IS_TESTING:
        analytics.track(
            event='TO_OrderPlaced',
            user_id=f'{customer.id}',
            properties={
                'order_id': order_id,
                'order_amount_total': f'{order.amount_total}',
                'customer_id': f'{customer.id}',
                'customer_email': customer.email,
                'shopify_customer_id': customer.external_customer_id,
                'shopify_order_id': f'{order.external_order_id}',
                'child_name': order.customer_child.first_name,
                'child_birthdate': order.customer_child.birth_date,
                'active_subscription': True,
                'recipes': [
                    {
                        'name': line_item.product.title,
                        'quantity': line_item.quantity,
                    } for line_item in order.line_items.filter()
                ]
            }
        )
        analytics.flush()


@shared_task(base=HttpErrorRetryTask)
def sync_order_payment_failed_to_analytics(order_id: str):
    Order = apps.get_model('orders', 'Order')
    order = Order.objects.get(id=order_id)
    if not settings.DEBUG and not settings.IS_TESTING:
        analytics.track(
            event='TO_PaymentDeclined',
            user_id=str(order.customer.id),
            properties={
                'active_subscription': True,
                'first_name': order.customer.first_name,
                'email': order.customer.email,
                'order_id': str(order.id),
                'child_name': order.customer_child.first_name,
            }
        )
        analytics.flush()


@shared_task(base=HttpErrorRetryTask)
def send_order_confirmation_email(order_id: str):
    Order = apps.get_model('orders', 'Order')
    order = Order.objects.get(id=order_id)
    subject = '🌱 Your Tiny Organics Order is Confirmed!'
    client = TaxProcessorClient()
    tax_response = client\
        .set_customer_discount(order.applied_discount)\
        .set_shipping_rate(order.shipping_rate)\
        .calculate_tax(order.customer_child.cart)
        
    context = {
        'customer': order.customer,
        'shipping_address': order.customer.addresses.first(),
        'domain': settings.SITE_URL,
        'line_items': order.line_items.filter(),
        'order': order,
        'is_24_pack': order.is_24_pack(),
        'tax_rate': round(tax_response.get('tax_rate'), 3)
    }
        
    if order.applied_discount:
        _running_subtotal = order.subtotal_amount
        _applied_discount_amount = _get_calculated_discount_amount(_running_subtotal, order)
        context['applied_discount_amount'] = Decimal(f'{_applied_discount_amount}')

    html_body = loader.render_to_string('emails/order-confirmation.html', context)
    text_body = ''
    send_email_message(
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        email_address=_scrub_email_address(order.customer.email)
    )

    return f'Done Sending Email to {order.customer}'

def _get_calculated_discount_amount(_running_subtotal, order):
    applied_discount_amount = Decimal('0')
    
    if order.is_24_pack():
        _running_subtotal = (order.subtotal_amount - Decimal('20'))
    if order.applied_discount.discount.discount_type == 'percentage':
        applied_discount_amount = (_running_subtotal * order.applied_discount.discount.amount) / 100
    else:
        applied_discount_amount = order.applied_discount.discount.amount

    return applied_discount_amount
