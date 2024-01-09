from django.contrib.admin import register

from apps.analytics.models import Pixel
from apps.core.admin import CoreAdmin


@register(Pixel)
class PixelAdmin(CoreAdmin):
    list_display = 'id', 'is_active', 'name',
