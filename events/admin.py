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
    list_editable = [
        'longitude',
        'latitude',
    ]
    ordering = ['name', 'longitude', 'latitude']
    list_per_page = 10


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass
