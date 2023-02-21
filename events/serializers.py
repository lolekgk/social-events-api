from recurrence.fields import RecurrenceField
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
            # 'events',
        ]


class LocationCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            'name',
            'longitude',
            'latitude',
            'country',
            'city',
            'street',
            'street_number',
            'zip_code',
        ]


class EventRetrieveSerializer(serializers.ModelSerializer):
    participants_number = serializers.SerializerMethodField()
    location = LocationRetrieveSerializer()

    def get_participants_number(self, obj: Event):
        return obj.participants.count()

    class Meta:
        model = Event
        fields = [
            'id',
            'name',
            'access',
            'description',
            'created_at',
            'organizers',  # TODO add nested user models?
            'participants',
            'participants_number',
            'start_time',
            'end_time',
            'location',
            'banner',
            'recurrences',
        ]


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    recurrences = RecurrenceField()
    banner = serializers.ImageField(
        default='default-banner.jpeg',
    )

    class Meta:
        model = Event
        fields = [
            'name',
            'access',
            'banner',
            'description',
            'start_time',
            'end_time',
            'location',
            'recurrences',
        ]

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        if start_time > end_time:
            raise serializers.ValidationError(
                'The end time must be later than the start time.'
            )
        return attrs
