from django.contrib import admin

from .models import Event, Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'longitude',
        'latitude',
        'country',
        'city',
    ]

    list_per_page = 10
    ordering = ['name', 'longitude', 'latitude']
    search_fields = [
        'name__istartswith',
        'country__istartswith',
        'city__istartswith',
    ]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_filter = ['status', 'access']
    autocomplete_fields = ['location']
