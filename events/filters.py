from django.db.models import Count
from django_filters.rest_framework import FilterSet, TypedChoiceFilter

from .models import Event, Location


class LocationFilter(FilterSet):
    has_events = TypedChoiceFilter(
        method="filter_has_events",
        label="Has events",
        choices=[(True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True",
    )

    class Meta:
        model = Location
        fields = ["has_events"]

    def filter_has_events(self, queryset, name, value):
        if value:
            return queryset.annotate(event_count=Count("events")).filter(
                event_count__gt=0
            )
        return queryset.annotate(event_count=Count("events")).filter(
            event_count=0
        )


class EventFilter(FilterSet):
    class Meta:
        model = Event
        fields = {"location_id": ["exact"]}
