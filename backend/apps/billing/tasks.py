from decimal import Decimal

import django_fsm
import stripe.error
from celery import shared_task
from chunkator import chunkator
from django.apps import apps
from sentry_sdk.utils import logger
from celery_app import app
import csv
import stripe

from apps.core.tasks import StripeErrorRetryTask
from libs.stripe_import_client import StripeImportClient


@shared_task(base=StripeErrorRetryTask, soft_time_limit=60 * 60)
def create_setupintents_for_newly_created_payment_methods_from_stripe():
    PaymentMethod = apps.get_model('billing', 'PaymentMethod')
    payment_methods_not_setup_for_future_use = PaymentMethod.objects.filter(
        setup_for_future_charges=False,
    ).order_by(
        'customer__email',
    ).prefetch_related(
        'customer',
    )

    client = StripeImportClient()
    for payment_method in payment_methods_not_setup_for_future_use:
        try:
            response = client.create_setupintent_with_payment_method_id(
                payment_method.payment_processor_payment_method_id,
                payment_method.customer.payment_provider_customer_id,
            )
            if response.status == 'succeeded':
                payment_method.setup_for_future_charges = True
                payment_method.is_valid = True
                payment_method.save()
                print(
                    f'successfully created setup intent for {payment_method}')
        except stripe.error.CardError as e:
            logger.error(e)
            payment_method.is_valid = False
            payment_method.save()
        except stripe.error.InvalidRequestError:
            continue

    return 'Completed setting payment methods up for future use'


@shared_task(base=StripeErrorRetryTask, soft_time_limit=60 * 60)
def import_customer_payment_method_data_from_stripe():
    Customer = apps.get_model('customers', 'Customer')
    PaymentProcessor = apps.get_model('billing', 'PaymentProcessor')
    PaymentMethod = apps.get_model('billing', 'PaymentMethod')
    try:
        stripe_payment_processor = PaymentProcessor.objects.get(name='Stripe')
    except PaymentProcessor.DoesNotExist:
        return 'Cannot Import without having setup the Stripe Payment Processor in Django Admin.'

    customers_without_payment_methods = Customer.objects.filter(
        payment_methods__isnull=True,
        payment_provider_customer_id__isnull=False,
    )
    client = StripeImportClient()
    for customer in chunkator(customers_without_payment_methods, 100):
        try:
            response = client.get_payment_method_with_stripe_customer_id(
                customer.payment_provider_customer_id)
            if response.get('data', []):
                data = response['data'][0]
                PaymentMethod.objects.get_or_create(
                    customer=customer,
                    payment_processor=stripe_payment_processor,
                    payment_processor_payment_method_id=data['id'],
                    last_four=data['card']['last4'],
                    expiration_date=f'{data["card"]["exp_year"]}-'
                                    f'{"0" if data["card"]["exp_month"] < 10 else ""}'
                                    f'{data["card"]["exp_month"]}-01'
                )
        except Exception as e:
            logger.error(e)

    create_setupintents_for_newly_created_payment_methods_from_stripe.delay()

    return 'Done importing payment methods'


@app.task
def import_stripe_refund_from_line(data):
    Charge = apps.get_model('billing', 'Charge')
    Refund = apps.get_model('billing', 'Refund')
    payment_intent = data.get('PaymentIntent ID')
    Customer = apps.get_model('customers', 'Customer')
    refund_amount = data.get('Amount')
    customer_email = data.get('Email')
    try:
        client = StripeImportClient()
        refund = client.create_refund({
            'payment_intent': payment_intent,
            'reason': 'duplicate',
        })
        if refund:
            customer = Customer.objects.filter(email=customer_email).first()
            if customer:
                payment_method = customer.payment_methods.filter().first()
                if payment_method:
                    Refund.objects.create(
                        payment_method=payment_method,
                        amount=Decimal(f'{refund_amount}'),
                        customer=customer
                    )
            print(f'created {refund}')
    except Charge.DoesNotExist:
        logger.error(
            f'payment intent {payment_intent} does not exist in the system')
    except django_fsm.TransitionNotAllowed as e:
        logger.error(
            f'refund failed, this is most likely because we have already refunded this order: {e}')
    except stripe.error.InvalidRequestError as e:
        logger.error(
            f'Fail to refund in stripe, this could be because transaction was already refunded: {e}')
    except Exception as e:
        logger.error(f'Refund failed, {e}')


@app.task
def import_refunds_from_file(decoded_file):
    reader = csv.DictReader(decoded_file)
    for line in reader:
        import_stripe_refund_from_line.delay(line)
