from rest_framework import serializers

from events.models import Event, Location


class LocationRetrieveSerializer(serializers.ModelSerializer):
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
            'events',
        ]


class LocationCreateUpdateSerializer(serializers.ModelSerializer):
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
        ]
