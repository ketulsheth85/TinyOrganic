import csv
from typing import Dict, List

from celery import shared_task
from django.apps import apps
from django.core.exceptions import MultipleObjectsReturned

from apps.orders.libs import OrderConfirmationEmailStatus
from apps.orders.libs import OrderPaymentStatusEnum
from celery_app import app

from libs import locking



def _get_child_data_from_metafields(metafields: List):
    _child_data = {}
    for metafield in metafields:
        if metafield['key'] == 'child_name':
            _child_data['child_name'] = metafield['value']
        if metafield['key'] == 'child_birthdate':
            _child_data['child_birthdate'] = metafield['value']
        if 'child_name' in _child_data and 'child_birthdate' in _child_data:
            break
    return _child_data


@app.task
def _save_customer_child_data(child_data: Dict):
    CustomerChild = apps.get_model('customers', 'CustomerChild')

    if CustomerChild.objects.filter(
        parent_id=child_data['parent_id'],
        first_name=child_data['child_name'],
        birth_date=child_data['child_birthdate'],
    ).exists():
        return f'{child_data["child_name"]} is already in the system. Skipping..'

    child = CustomerChild.objects.create(
        parent_id=child_data['parent_id'],
        first_name=child_data['child_name'],
        birth_date=child_data['child_birthdate'],
    )

    return f'Imported {child}'


def _create_customer_records_from_line_data(data: Dict):
    Customer = apps.get_model('customers', 'Customer')
    CustomerChild = apps.get_model('customers', 'CustomerChild')
    Cart = apps.get_model('carts', 'Cart')

    try:
        customer = Customer.objects.get(email__iexact=data['email'])
    except Customer.DoesNotExist:
        customer = Customer(
            email=data['email'], first_name=data['first_name'], last_name=data['last_name'])
    except MultipleObjectsReturned:
        return 'Already Imported'

    if not customer.recharge_customer_id:
        customer.recharge_customer_id = data['customer_id']
        customer.save()
    if not customer.external_customer_id:
        customer.first_name = data['first_name']
        customer.last_name = data['last_name']
        customer.external_customer_id = data['external_customer_id']
        if bool(int(data['number_active_subscriptions'])):
            customer.has_active_subscriptions = True
            customer.status = 'subscriber'
        else:
            customer.status = 'deactivated'
        customer.save()
        print(f'created new customer: {customer}')

        if not customer.children.count():
            child, _ = CustomerChild.objects.get_or_create(
                parent=customer,
                first_name=f"{customer.first_name}'s Little One",
                last_name=customer.last_name,
            )

            if not child.cart:
                cart, _ = Cart.objects.get_or_create(
                    customer=customer,
                    customer_child=child,
                )
            print(f'create {child} for {customer}')


@shared_task
def create_customers_from_file(decoded_file):
    reader = csv.DictReader(decoded_file)
    for line in reader:
        _create_customer_records_from_line_data(line)


def _create_customer_subscription_from_line_data(data: Dict):
    Customer = apps.get_model('customers', 'Customer')
    CustomerChild = apps.get_model('customers', 'CustomerChild')
    Cart = apps.get_model('carts', 'Cart')
    CartLineItem = apps.get_model('carts', 'CartLineItem')
    CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')
    ProductVariant = apps.get_model('products', 'ProductVariant')

    try:
        customer = Customer.objects.get(email__iexact=data['customer_email'])
        customer_child = customer.children.first()
        if not customer_child:
            customer_child, _ = CustomerChild.objects.get_or_create(
                parent=customer,
                first_name=f"{customer.first_name}'s Little One"
            )

        cart, _ = Cart.objects.get_or_create(
            customer=customer,
            customer_child=customer_child,
        )

        subscription = CustomerSubscription.objects.filter(
            customer=customer,
            customer_child=customer_child,
        ).first()
        if not subscription:
            subscription, _ = CustomerSubscription.objects.get_or_create(
                customer=customer,
                customer_child=customer_child,
                defaults={
                    'is_active': False if data.get('cancelled_at', False) else 'active',
                    'status': 'inactive' if data.get('cancelled_at', False) else 'active',
                    'frequency': data['charge_interval_frequency'],
                    'deactivated_at': data['cancelled_at'] if data['cancelled_at'] else None,
                    'number_of_servings': '12' if data['recurring_price'] == '5.49' else '24',
                },
            )

            variant = ProductVariant.objects.filter(
                external_variant_id=data['external_variant_id']).first()
            if variant:
                line_item, _ = CartLineItem.objects.get_or_create(
                    cart=cart,
                    product_variant=variant,
                    product=variant.product,
                    defaults={
                        'quantity': data['quantity'],
                    }
                )
                print(f'created line item for cart: {cart}')
    except Customer.DoesNotExist:
        print(f"No customer with email {data['customer_email']}")
    except MultipleObjectsReturned:
        print(f'{data["customer_email"]} already exists')


@shared_task
def create_subscriptions_from_file(decoded_file):
    reader = csv.DictReader(decoded_file)
    for line in reader:
        _create_customer_subscription_from_line_data(line)


@app.task
def update_next_order_charge_dates_from_file(decoded_file):
    reader = csv.DictReader(decoded_file)
    Customer = apps.get_model('customers', 'Customer')

    for line in reader:
        try:
            customer = Customer.objects.get(email=line['Row Labels'])
            with locking.acquire_shared_lock_context(
                f'update-subscriptions-for-customer-{customer.id}',
                'celery',
            ):
                for subscription in customer.active_subscriptions():
                    with locking.acquire_shared_lock_context(
                        f'update-subscription-{subscription.id}',
                        'celery',
                        timeout=60,
                    ):
                        subscription.next_order_charge_date = line['New Date']
                        subscription.save()
                        subscription.refresh_from_db()
                        print(
                            f'Updated {subscription}. Next Order changes enabled date: '
                            f'{subscription.next_order_changes_enabled_date}'
                        )
        except Customer.DoesNotExist:
            print(
                f'Customer with email: {line["Row Labels"]} does not exist. skipping to next line')
            continue

    return 'Completed updating next order charge dates for customers.'


@app.task
def send_confirmation_email_from_file(decoded_file):
    Order = apps.get_model('orders', 'Order')
    reader = csv.DictReader(decoded_file)
    
    for line in reader:
        try:
            order_id = line.get('ID')
            order = Order.objects.get(id=order_id)        
            if order.payment_status == OrderPaymentStatusEnum.paid:
                if order.order_confirmation_email_status != OrderConfirmationEmailStatus.sent:
                    order.send_confirmation_email()
                else:
                    print(f'Looks like an email was already sent to order ID: {order_id}.')
                    continue
            else:
                print(f'Looks like order ID: {order_id} still owes money 💰 no confirmation email sent.')
                continue
        
        except Order.DoesNotExist:
            print(f'Order ID: {order_id} does not exist please review your CSV.')
            continue
    return 'Completed sending confirmation emails from CSV file.'
