import csv
from decimal import Decimal
from time import sleep

from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.utils import timezone

from apps.core.tasks import HttpErrorRetryTask
from celery_app import app
from libs import celery_helpers, locking

from libs.yotpo_client import YotpoClient, LoyaltyProgramCustomer, CouldNotGetYotpoCustomerError


@shared_task
def deactivate_expired_discount_codes():
    Discount = apps.get_model('discounts', 'Discount')
    for discount in Discount.objects.filter(is_active=True, deactivate_at__lte=timezone.now()):
        discount.is_active = False
        discount.save()

# TODO ask Raul why is this task running? Potential Bug 🦟
# @shared_task
# def activate_inactive_discount_codes():
#     Discount = apps.get_model('discounts', 'Discount')
#     for discount in Discount.objects.filter(is_active=False, activate_at__lte=timezone.now()):
#         discount.is_active = True
#         discount.save()


@app.task
def import_discount_code_from_line(data):
    CustomerDiscount = apps.get_model('discounts', 'CustomerDiscount')
    Discount = apps.get_model('discounts', 'Discount')
    discount, created = Discount.objects.get_or_create(
        codename=data['code'].upper(),
        discount_type=data['discount_type'].replace('_', ' ').lower(),
        is_active=data['status'] == 'enabled',
        amount=data['value'],
        activate_at=data['starts_at'] if data['starts_at'] else timezone.now(),
        deactivate_at=data['ends_at'] if data['ends_at'] else None,
        redemption_limit_per_customer=data.get('usage_limit', 1),
        redemption_count=data.get('times_used', 0),
    )
    if created:
        customer_discounts = CustomerDiscount.objects.filter(
            discount__codename=discount.codename,
        )
        _discount = None
        for customer_discount in customer_discounts:
            if customer_discount.discount != discount:
                old_discount = customer_discount.discount
                customer_discount.discount = discount
                customer_discount.save()
                _discount = Discount.objects.filter(id=old_discount.id)
                print(f'Replaced {customer_discount.discount} with {discount}')
        if _discount:
            _discount.delete()


@app.task
def import_discount_codes_from_file(decoded_file):
    reader = csv.DictReader(decoded_file)
    for line in reader:
        import_discount_code_from_line.delay(line)


def _create_new_loyalty_customer(customer):
    client = YotpoClient()
    customer_dto = LoyaltyProgramCustomer(
        id=str(customer.id),
        email=customer.email,
        first_name=customer.first_name,
        last_name=customer.last_name
    )
    client.create_customer(customer_dto)
    if not settings.TESTING:
        sleep(4)
    yotpo_customer = client.get_customer(str(customer.id))
    return yotpo_customer


def _fetch_loyalty_customer(customer):
    client = YotpoClient()
    try:
        loyalty_customer = client.get_customer(str(customer.id))
    except CouldNotGetYotpoCustomerError:
        loyalty_customer = _create_new_loyalty_customer(customer)
    return loyalty_customer


@shared_task(base=HttpErrorRetryTask, rate_limit='2/s')
def create_customer_referral_coupon_from_loyalty_client(customer_id):
    Customer = apps.get_model('customers', 'Customer')
    customer = Customer.objects.get(id=customer_id)
    with locking.acquire_shared_lock_context(
        f'create_customer_referral_coupon_from_loyalty_client-{customer.id}', 'celery'
    ):

        loyalty_customer = _fetch_loyalty_customer(customer)
        discount_code = loyalty_customer.get('referral_code').get('code')
        Discount = apps.get_model('discounts', 'Discount')
        try:
            yotpo_discount = Discount.objects.get(codename=discount_code)
            yotpo_discount.from_yotpo = True
            yotpo_discount.save()
        except Discount.DoesNotExist:
            Discount.objects.create(
                codename=discount_code,
                referrer=customer,
                discount_type='fixed amount',
                amount=Decimal('30.00'),
                banner_text=f"Save $30 on your first order with {customer.first_name}'s referral code: {discount_code}",
                is_active=True,
                from_yotpo=True
            )


@shared_task
@celery_helpers.prevent_multiple
def create_yotpo_referral_discount_for_customers_without_referral_discount():
    Customer = apps.get_model('customers', 'Customer')

    customers_without_referral_discount = Customer.objects\
        .filter(referral_discount_codes__isnull=True)[:40]

    errors = []
    for customer in customers_without_referral_discount:
        try:
            create_customer_referral_coupon_from_loyalty_client(customer.id)
        except Exception as e:
            errors.append(e)

    if errors:
        raise Exception(errors)


@shared_task
@celery_helpers.prevent_multiple
def create_yotpo_referral_discount_for_customers_with_non_yotpo_referral_discount():
    Discount = apps.get_model('discounts', 'Discount')

    non_yotpo_referral_discounts = Discount.objects\
        .filter(from_yotpo=False, referrer__isnull=False)[:40]

    errors = []
    for discount in non_yotpo_referral_discounts:
        try:
            create_customer_referral_coupon_from_loyalty_client(
                discount.referrer.id)
        except Exception as e:
            errors.append(e)

    if errors:
        raise Exception(errors)
