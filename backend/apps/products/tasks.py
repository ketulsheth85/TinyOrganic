from datetime import timedelta

from celery import shared_task
from django.db.models import Q
from sentry_sdk.utils import logger

from apps.products.libs import MealPlanRecommendationEngine
from celery_app import app
from django.apps import apps
from django.utils import timezone


@app.task
def _replace_cart_line_item(cart_id: str, product_id: str):
    Cart = apps.get_model('carts', 'Cart')
    CartLineItem = apps.get_model('carts', 'CartLineItem')
    Product = apps.get_model('products', 'Product')
    product = Product.objects.get(id=product_id)

    cart = Cart.objects.get(id=cart_id)
    line_item_to_replace = cart.line_items.filter(product=product)
    sku_id_postfix = line_item_to_replace.first().product_variant.sku_id[-2:]
    # 1: Is there another recipe in the cart with the same price?
    other_line_items = cart.line_items.filter(
        ~Q(product=product),
        product_variant__sku_id__icontains=sku_id_postfix,
        product__product_type='recipe',
    ).order_by('product_variant__price')
    if (
        other_line_items.exists()
        and other_line_items.first().product_variant.price <= line_item_to_replace.first().product_variant.price
    ):
        # 2: If there is, let's update its quantity
        if other_line_items.exists():
            existing_line_item_with_equal_price = other_line_items.first()
            existing_line_item_with_equal_price.quantity += line_item_to_replace.first().quantity
            existing_line_item_with_equal_price.save()
    else:
        # 3: If not, let's find another recipe that suits our needs
        engine = MealPlanRecommendationEngine(child=cart.customer_child).run()
        new_product = None
        for recommended_product_data in engine.recommendations['remaining_products']:
            recommended_product = Product.objects.get(id=recommended_product_data['recipe_id'])
            # 4: Let's ensure that we're not selecting the product we're trying to replace
            if recommended_product != product:
                new_product = recommended_product
                break

        if not new_product:
            for recommended_product_data in engine.recommendations['recommendations']:
                recommended_product = Product.objects.get(id=recommended_product_data['recipe_id'])
                # 4: Let's ensure that we're not selecting the product we're trying to replace
                if recommended_product != product:
                    new_product = recommended_product
                    break

        # 5: If there's another valid recommended recipe, let's create the cart line item
        if new_product:
            CartLineItem.objects.create(
                product=new_product,
                product_variant=new_product.variants.filter(
                    sku_id__icontains=sku_id_postfix,
                ).first(),
                quantity=line_item_to_replace.first().quantity,
                cart=cart,
            )
        else:
            logger.error(f'Cannot find a suitable product replacement for {cart}')

    # 6: delete the line item to replace
    line_item_to_replace.delete()

    return f'Replaced items for: {cart}'


@app.task
def replace_product_in_cart_line_items_for_inactive_subscribers(product_id: str):
    Cart = apps.get_model('carts', 'Cart')
    for cart in Cart.objects.filter(
        line_items__isnull=False,
        line_items__product_id__in=[product_id, ],
        customer_child__subscription__is_active=False,
    ):
        _replace_cart_line_item.delay(cart.id, product_id)

    return f'Sent all inactive cart line items to be replaced'


@shared_task
def replace_product_in_cart_line_items_for_active_subscribers(product_id: str):
    Cart = apps.get_model('carts', 'Cart')

    for cart in Cart.objects.filter(
        line_items__isnull=False,
        line_items__product_id__in=[product_id, ],
        customer_child__subscription__is_active=True,
    ):
        _replace_cart_line_item.delay(cart.id, product_id)

    replace_product_in_cart_line_items_for_inactive_subscribers.delay(product_id)

    return f'Sent all Cart Line Items to be replaced'


@shared_task
def deactivate_products_set_to_deactivate_today():
    Product = apps.get_model('products', 'Product')

    for product in Product.objects.filter(is_active=True, deactivation_date=timezone.now().date()):
        product.is_active = False
        product.reactivation_date = timezone.now() + timedelta(days=365)
        product.deactivation_date = None
        product.save()

    return 1


@shared_task
def activate_products_set_to_activate_today():
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.filter(is_active=False, reactivation_date=timezone.now().date()):
        product.is_active = True
        product.reactivation_date = None
        product.save()

    return 'Done reactivating products'
