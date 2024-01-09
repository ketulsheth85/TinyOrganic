import csv
from datetime import datetime
from typing import Dict

from django.apps import apps
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from apps.core.views import CoreUploadCSVView
from celery_app import app


@app.task
def _create_order_line_item_with_data(data: Dict):
    Order = apps.get_model('orders', 'Order')
    Customer = apps.get_model('customers', 'Customer')
    CustomerChild = apps.get_model('customers', 'CustomerChild')
    OrderLineItem = apps.get_model('orders', 'OrderLineItem')
    ProductVariant = apps.get_model('products', 'ProductVariant')
    Cart = apps.get_model('carts', 'Cart')
    CartLineItem = apps.get_model('carts', 'CartLineItem')
    CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')
    try:
        variant = ProductVariant.objects.get(sku_id=data['Lineitem sku'])

        try:
            customer = Customer.objects.get(email__iexact=data['Email'])
        except Customer.DoesNotExist:
            customer, _ = Customer.objects.get_or_create(
                last_name=data['Shipping Name'].split(' ')[1],
                first_name=data['Shipping Name'].split(' ')[0],
                email=data['Email'],
            )

        customer_child = customer.children.first()
        if not customer_child:
            customer_child, _ = CustomerChild.objects.get_or_create(
                parent=customer,
                first_name=f'{customer.first_name}\' Little One',
            )

        cart, _ = Cart.objects.get_or_create(
            customer=customer,
            customer_child=customer_child,
        )
        CartLineItem.objects.get_or_create(
            cart=cart,
            product_variant=variant,
            product=variant.product,
            defaults={'quantity': data['Lineitem quantity']},
        )

        try:
            order = Order.objects.get(
                external_order_id=data['Id'],
            )
        except Order.DoesNotExist:
            order = Order(
                customer=customer,
                customer_child=customer.children.first(),
            )
            customer.has_active_subscriptions = True
            customer.status = 'subscriber'
            customer.save()

        order.external_order_id = data['Id']
        if data['Tags']:
            order.tags = data['Tags'].split()
        if data['Total']:
            order.amount_total = data.get("Total", 0) if len(data['Total']) else 0
            order.charged_amount = data.get("Total", 0) if len(data['Total']) else 0
        if data['Taxes']:
            order.tax_total = data.get("Taxes", 0) if len(data['Taxes']) else 0
        if data['Financial Status']:
            order.payment_status = data['Financial Status']
        if data['Name']:
            order.order_number = data['Name'].replace('#', '')
        if data['Fulfillment Status']:
            order.fulfillment_status = data['Fulfillment Status']
        if data['Paid at']:
            order.charged_at = datetime.strptime(data['Paid at'], '%Y-%m-%d %H:%M:%S %z')
        order.fulfillment_status = 'pending' if data['Fulfillment Status'] == 'unfulfilled' else \
            data['Fulfillment Status']

        order.save()
        if order.charged_at and not customer.active_subscriptions().count():
            CustomerSubscription.objects.create(
                customer=order.customer,
                customer_child=order.customer_child,
                is_active=True,
                status='active',
            )

        OrderLineItem.objects.get_or_create(
            product_variant=variant,
            product=variant.product,
            order=order,
            defaults={
                'quantity': data['Lineitem quantity'],
            }
        )
    except ProductVariant.DoesNotExist:
        print("Could not find product with sku", data['Lineitem sku'])


@app.task
def create_line_items(decoded_file):
    reader = csv.DictReader(decoded_file)
    for line in reader:
        _create_order_line_item_with_data(line)


@method_decorator(staff_member_required, name='dispatch')
class UploadShopifyOrdersCSVView(CoreUploadCSVView):
    template_name = 'upload_orders_from_shopify.html'
    async_function = create_line_items
    view_name = 'upload-order-csv'


