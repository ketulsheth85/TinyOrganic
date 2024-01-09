from decimal import Decimal
from django.contrib import admin
from django.contrib.admin import register
from django.shortcuts import redirect
from django.urls import path, reverse
from django.conf import settings

from apps.core.admin import CoreAdmin
from apps.products.models import Product as TinyProduct
from apps.products.models import ProductVariant
from libs.shopify_rest_client import ShopifyRestClient


readonly_fields = ['id']
list_display = ['id', 'title', 'is_active', 'product_type']
if not settings.RECURRING_ITEMS_TOGGLE_ENABLED:
    readonly_fields = readonly_fields + ['is_recurring']
    list_display = list_display + ['is_recurring']

if not settings.SHOW_VARIANTS_ENABLED:
    readonly_fields = readonly_fields + ['show_variants']
    list_display = list_display + ['show_variants']


class ProductVariantAdminInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


@register(TinyProduct)
class ProductAdmin(CoreAdmin):
    change_list_template = "admin/products/product_changelist.html"
    readonly_fields = readonly_fields
    ordering = 'title',
    inlines = ProductVariantAdminInline,
    list_display = list_display + ['available_fulfillment_centers']
    search_fields = 'id', 'title', 'product_type', 'fulfillment_centers__location'

    # Optimize list display by prefetching
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('fulfillment_centers')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('products/sync/', self.sync_products_from_shopify, name='sync_products_from_shopify'),
        ]
        return my_urls + urls

    def available_fulfillment_centers(self, obj):
        return ", ".join([w.location for w in obj.fulfillment_centers.filter()])

    def sync_products_from_shopify(self, _):
        shopify_rest_client = ShopifyRestClient()
        products = shopify_rest_client.get_products()

        for product_data in products:
            product, _ = TinyProduct.objects.get_or_create(
                external_product_id=product_data['id'],
                title=product_data['title'],
                product_type=product_data['product_type'],
                defaults={
                    'is_active': product_data['status'] == 'active',
                    'image_url': product_data['images'][0]['src'] if product_data['images'] else '',
                    'from_production_shopify_store': True,
                    'tags': product_data['tags'].split(',') if product_data['tags'] else []
                }
            )
            if product.product_type not in {'recipe', 'add-on'}:
                if product.is_active:
                    continue
                product.is_active = False
                product.save()
                continue
            if 'auto' in product.title.lower():
                product.is_active = False
                product.save()
                product.delete()
                continue
            for variant in product_data['variants']:
                '''
                Temporarily add product variant title outside of query to prevent duplicates
                '''
                product_variant = ProductVariant.objects.get_or_create(
                    product=product,
                    external_variant_id=variant['id'],
                    defaults={
                        'price': Decimal(f'{variant["price"]}'),
                        'sku_id': variant['sku'],
                    },
                )[0]
                product_variant.title = variant['option1']
                product_variant.save()
        return redirect(reverse('admin:products_product_changelist'))
