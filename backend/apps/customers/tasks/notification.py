import analytics
from celery import shared_task
from django.apps import apps
from django.conf import settings

from apps.core.tasks import HttpErrorRetryTask
from libs import locking


@shared_task(base=HttpErrorRetryTask)
def sync_subscription_cancelled_event(subscription_id: str):
    CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')

    with locking.acquire_shared_lock_context(
        f'sync-subscription-cancelled-event-{subscription_id}',
        'celery',
    ):
        subscription = CustomerSubscription.objects.get(id=subscription_id)
        customer = subscription.customer
        cart = subscription.customer_child.cart
        if not settings.IS_TESTING and not settings.DEBUG:
            child = subscription.customer_child
            line_items_list = list(cart.line_items.filter().order_by(
                'product__title'
            ).values_list(
                'product__title', flat=True
            ))
            analytics.identify(
                str(customer.id),
                {
                    'email': customer.email,
                    'active_subscription': False,
                    'tags': ['Unsubscribed Customer'],
                    'subscription_product': line_items_list,
                    'cancelled_subscription_at': subscription.deactivated_at,
                }
            )
            customer_address = customer.addresses.first()
            analytics.track(
                str(customer.id),
                'Cancelled Subscription',
                properties={
                    'customer_id': str(customer.id),
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'email': customer.email,
                    'active_subscription': True,
                    'child_name': child.first_name,
                    'child_birthdate': child.birth_date,
                    'allergies': list(child.allergies.filter().values_list('name', flat=True)),
                    'pack_size': subscription.number_of_servings,
                    'order_count': customer.number_of_orders,
                    'total_spent': f'{customer.amount_spent}',
                    'order_frequency': subscription.frequency,
                    'shipping_city': customer_address.city if customer_address and customer_address.city else '',
                    'shipping_state': customer_address.state if customer_address and customer_address.state else '',
                    'zip_code': customer_address.zipcode if customer_address and customer_address.zipcode else '',
                    'subscription_product': line_items_list,
                    'activated_subscription_at': subscription.activated_at,
                    'cancelled_subscription_at': subscription.deactivated_at,
                }
            )

            analytics.flush()
            subscription.synced_to_klaviyo = True
            subscription.updated_profile_fields_to_klaviyo = True
            subscription.save()
            return 'Will sync to segment in batches of 100, for scalability'


@shared_task(base=HttpErrorRetryTask)
def sync_subscription_activated_event(subscription_id: str):
    CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')

    with locking.acquire_shared_lock_context(
        f'sync-subscription-activated-event-{subscription_id}',
        'celery',
        timeout=60
    ):
        subscription = CustomerSubscription.objects.get(id=subscription_id)
        customer = subscription.customer
        if not settings.IS_TESTING and not settings.DEBUG:
            cart = subscription.customer_child.cart
            child = subscription.customer_child
            line_items_list = list(cart.line_items.filter().order_by(
                'product__title'
            ).values_list(
                'product__title', flat=True
            ))
            analytics.identify(
                str(customer.id),
                {
                    'email': customer.email,
                    'active_subscription': True,
                    'tags': ['Active Subscriber'],
                    'subscription_product': line_items_list,
                    'activated_subscription_at': subscription.activated_at,
                }
            )
            customer_address = customer.addresses.first()
            analytics.track(
                str(customer.id),
                'Started Subscription',
                properties={
                    'customer_id': str(customer.id),
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'email': customer.email,
                    'active_subscription': True,
                    'child_name': child.first_name,
                    'child_birthdate': child.birth_date,
                    'allergies': list(child.allergies.filter().values_list('name', flat=True)),
                    'pack_size': subscription.number_of_servings,
                    'order_count': customer.number_of_orders,
                    'total_spent': f'{customer.amount_spent}',
                    'order_frequency': subscription.frequency,
                    'shipping_city': customer_address.city if customer_address and customer_address.city else '',
                    'shipping_state': customer_address.state if customer_address and customer_address.state else '',
                    'zip_code': customer_address.zipcode if customer_address and customer_address.zipcode else '',
                    'subscription_product': line_items_list,
                    'activated_subscription_at': subscription.activated_at,
                }
            )
            analytics.flush()
            subscription.synced_to_klaviyo = True
            subscription.updated_profile_fields_to_klaviyo = True
            subscription.save()
            return 'Will sync to segment in batches of 100, for scalability'


@shared_task(base=HttpErrorRetryTask)
def sync_subscription_created_event(subscription_id:  str):
    CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')

    with locking.acquire_shared_lock_context(
        f'sync-subscription-created-event-{subscription_id}',
        'celery',
        timeout=60,
    ):
        subscription = CustomerSubscription.objects.get(id=subscription_id)
        customer = subscription.customer
        if not settings.IS_TESTING and not settings.DEBUG:
            analytics.identify(
                str(customer.id),
                {
                    'email': customer.email,
                    'active_subscription': subscription.is_active,
                    'tags': ['New Lead'],
                    'subscription_product': [],
                    'activated_subscription_at': None,
                }
            )
            customer_address = customer.addresses.first()
            analytics.track(
                str(customer.id),
                'New Customer',
                properties={
                    'customer_id': str(customer.id),
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'email': customer.email,
                    'active_subscription': subscription.is_active,
                    'child_name': subscription.customer_child.first_name,
                    'subscription_product': [],
                    'activated_at': subscription.activated_at,
                    'shipping_city': customer_address.city if customer_address and customer_address.city else '',
                    'shipping_state': customer_address.state if customer_address and customer_address.state else '',
                    'zip_code': customer_address.zipcode if customer_address and customer_address.zipcode else '',
                },
                integrations={
                    'all': False,
                    'Klaviyo': True,
                }
            )
            analytics.flush()
            subscription.synced_to_klaviyo = True
            subscription.updated_profile_fields_to_klaviyo = True
            return f'Synced subscription created event for {customer}'


@shared_task(base=HttpErrorRetryTask)
def sync_klaviyo_profile_fields_event(subscription_id: str):
    CustomerSubscription = apps.get_model('customers', 'CustomerSubscription')

    with locking.acquire_shared_lock_context(
        f'sync-klaviyo-profile-fields-event-{subscription_id}',
        'celery',
        timeout=60
    ):
        subscription = CustomerSubscription.objects.get(id=subscription_id)
        customer = subscription.customer
        if not settings.IS_TESTING and not settings.DEBUG:
            cart = subscription.customer_child.cart
            line_items_list = list(cart.line_items.filter().order_by(
                'product__title'
            ).values_list(
                'product__title', flat=True
            ))
            child = subscription.customer_child
            analytics.identify(
                str(customer.id),
                {
                    'email': customer.email,
                    'active_subscription': subscription.is_active,
                    'tags': ['Active Subscriber'] if subscription.is_active else ['Unsubscribed Customer'],
                    'subscription_product': line_items_list,
                    'activated_subscription_at': subscription.activated_at,
                    'cancelled_subscription_at': subscription.deactivated_at,
                }
            )
            customer_address = customer.addresses.first()

            analytics.track(
                str(customer.id),
                'Updating Profile',
                properties={
                    'customer_id': str(customer.id),
                    'first_name': customer.first_name,
                    'last_name': customer.last_name,
                    'email': customer.email,
                    'active_subscription': subscription.is_active,
                    'child_name': child.first_name,
                    'child_birthdate': child.birth_date,
                    'allergies': list(child.allergies.filter().values_list('name', flat=True)),
                    'pack_size': subscription.number_of_servings,
                    'order_count': customer.number_of_orders,
                    'total_spent': f'{customer.amount_spent}',
                    'order_frequency': subscription.frequency,
                    'shipping_city': customer_address.city if customer_address and customer_address.city else '',
                    'shipping_state': customer_address.state if customer_address and customer_address.state else '',
                    'zip_code': customer_address.zipcode if customer_address and customer_address.zipcode else '',
                    'subscription_product': line_items_list,
                    'activated_subscription_at': subscription.activated_at,
                    'cancelled_subscription_at': subscription.deactivated_at,
                }
            )
            analytics.flush()
            subscription.synced_to_klaviyo = True
            subscription.updated_profile_fields_to_klaviyo = True
            subscription.save()
            return 'Will sync to segment in batches of 100, for scalability'
