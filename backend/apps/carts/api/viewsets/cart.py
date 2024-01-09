from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.viewsets import mixins

from apps.carts.api.serializers import CartReadOnlySerializer, CartWriteSerializer
from apps.carts.models import Cart, CartLineItem
from apps.products.models import Product, ProductVariant


class CartViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Cart.objects.filter()
    serializer_class = CartReadOnlySerializer

    def get_serializer_class(self):
        if self.request.method in {'PUT', 'PATCH'}:
            return CartWriteSerializer
        return self.serializer_class

    def get_queryset(self):
        """
        get_queryset() - Carts

        This method will attempt to read the `customer` key/value pair in the querystring.
        If it does not exist, then the method will check if the current user exists and if the
        current user is a superuser of the system. If not, then it will return an empty list.
        """
        customer_id = self.request.query_params.get('customer', None)

        if not customer_id and not self.request.user and not self.request.user.is_superuser:
            return self.queryset.none()

        return self.queryset.filter(customer_id=customer_id)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        requested_line_items = request.data.get('line_items')
        if requested_line_items:
            instance.line_items.filter().delete()

        for line_item in requested_line_items:
            # step 2: get the correct product with proper sku id based on the subscription's # of servings
            product = Product.objects.get(id=line_item['product']['id'])
            if product.product_type != 'recipe':
                product_variant = ProductVariant.objects.get(
                    id=line_item['product_variant']['id']
                )
            else:
                product_variant = ProductVariant.objects.get(
                    product=product,
                    sku_id__iendswith=f'-{instance.customer_child.subscription.number_of_servings}'
                )
            try:
                cart_line_item = CartLineItem.objects.get(
                    cart=instance,
                    product=product,
                    product_variant=product_variant
                )
            except CartLineItem.DoesNotExist:
                cart_line_item = CartLineItem.objects.create(
                    cart=instance,
                    product=product,
                    product_variant=product_variant,
                )

            quantity = line_item.get('quantity', None)
            if quantity is not None:
                if quantity > 0:
                    cart_line_item.quantity = quantity
                    cart_line_item.save()
                else:
                    cart_line_item.delete()

        instance.refresh_from_db()
        return Response(self.serializer_class(instance=instance).data)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
