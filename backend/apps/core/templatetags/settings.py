from django import template
from django.conf import settings

register = template.Library()


@register.filter
def setting(setting, key=None):
    value = getattr(settings, setting)
    if key:
        value = value[key]
    return value
