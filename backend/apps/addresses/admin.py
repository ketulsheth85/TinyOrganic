from django.contrib import admin

from apps.addresses.models import Location


# Register your models here.
class LocationAdmin(admin.ModelAdmin):
    raw_id_fields = 'customer',
    search_fields = 'id', 'customer__email', 'zipcode',
    list_display = 'id', 'customer', 'city', 'state', 'zipcode',


admin.site.register(Location, LocationAdmin)
