from rest_framework import serializers

from events.models import Event, Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            'id',
            'name',
            'longitude',
            'latitude',
            'country',
            'city',
            'street',
            'street_number',
            'zip_code',
            'event_set',
        ]
