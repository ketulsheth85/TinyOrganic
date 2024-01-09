from django.apps import apps

from libs.helpers import ModelChoiceEnum


class DiscountRuleTypeEnum(ModelChoiceEnum):
    minimum_price = 'Minimum Price'
    product = 'Product'
    number_of_orders = 'Number of Orders'
    customer_set = 'Customer Set'
    nth_time_subscribers = 'Nth-time Subscribers'


class CannotCreateDiscountForCustomerError(Exception):
    ...


class CustomerDiscountStatusEnum:
    unredeemed = 'unredeemed'
    redeemed = 'redeemed'


class DiscountBuilder:
    def __init__(self, ):
        self.discount = None
        self.carts = []
        self.redemption_limit = None
        self.customer_discounts = []
        self.customer = None

    def set_discount(self, discount: 'Discount') -> 'DiscountBuilder':
        self.discount = discount
        return self

    def set_customer(self, customer: 'Customer'):
        self.customer = customer
        return self

    def add_cart(self, cart: 'Cart') -> 'DiscountBuilder':
        self.carts.append(cart)
        return self

    def _is_customer_eligible(self, cart: 'Cart') -> bool:
        is_eligible = False

        rules = self.discount.rules.filter(is_active=True)
        if rules.exists():
            for rule in rules:
                if rule.type == DiscountRuleTypeEnum.minimum_price:
                    is_eligible = cart.subtotal >= rule.minimum_cart_amount
                elif rule.type == DiscountRuleTypeEnum.customer_set:
                    is_eligible = rule.apply_to_customers.filter(
                        id=cart.customer.id).exists()
                elif rule.type == DiscountRuleTypeEnum.product:
                    is_eligible = rule.apply_to_products.filter(
                        id__in=cart.line_items.filter().values_list(
                            'product__id', flat=True
                        )
                    ).exists()
                elif rule.type == DiscountRuleTypeEnum.nth_time_subscribers:
                    is_eligible = cart.customer_child.orders.count() + 1 == rule.nth_time_subscriber
                elif rule.type == DiscountRuleTypeEnum.number_of_orders:
                    is_eligible = True
                    self.redemption_limit = rule.number_of_orders

                if is_eligible is False:
                    break
        else:
            is_eligible = self.discount.is_active

        return is_eligible

    def _remove_existing_discounts(self):
        CustomerDiscount = apps.get_model('discounts', 'CustomerDiscount')
        CustomerDiscount.objects.filter(
            customer=self.customer,
            status=CustomerDiscountStatusEnum.unredeemed,
        ).delete()

    def _create_discount(self, child: 'CustomerChild'):
        CustomerDiscount = apps.get_model('discounts', 'CustomerDiscount')
        customer_discount, _ = CustomerDiscount.objects.get_or_create(
            customer=child.parent,
            customer_child=child,
            discount=self.discount
        )
        self.customer_discounts.append(customer_discount)

    def build(self):
        self._remove_existing_discounts()
        if not self.discount or len(self.carts) == 0:
            raise CannotCreateDiscountForCustomerError(
                'Cannot create a discount for customer without a discount code and cart'
            )
        if self.discount.discount_type == 'fixed amount':
            if self._is_customer_eligible(self.carts[0]):
                first_child = self.carts[0].customer_child
                self._create_discount(first_child)
        else:
            for cart in self.carts:
                if self._is_customer_eligible(cart):
                    child = cart.customer_child
                    self._create_discount(child)

        if not self.customer_discounts:
            raise CannotCreateDiscountForCustomerError(
                'No items in your subscription(s) are eligible for this discount'
            )

        if self.discount.referrer:
            if str(self.discount.referrer.id) == str(self.carts[0].customer.id):
                raise CannotCreateDiscountForCustomerError(
                    'Discount referrer cannot be the same as customer applying discount '
                    f'discount: {self.discount} '
                    f'customer: {self.customer}'
                )

        return self
