from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import EventFilter, LocationFilter
from .models import Event, Location
from .pagination import DefaultPagination
from .serializers import (
    EventCreateUpdateSerializer,
    EventRetrieveSerializer,
    LocationCreateUpdateSerializer,
    LocationRetrieveSerializer,
)


class EventOrganizerListView:
    pass


class EventOrganizerDetailView:
    pass


class EventParticipantListView:
    pass


class EventParticipantDetailView:
    pass


class EventInvitationListView:
    pass


class EventIvitationDetailView:
    pass


class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()  # TODO show only event's, that user can see
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]  # TODO filter by participants number, location(Custom filter), access(open, closed), status,
    # TODO reccurring every week, itp., check if it's possible to add searchfield to location filter
    filterset_class = EventFilter
    ordering_fields = ["name", "start_time"]
    search_fields = [
        "name",
        "location__city",
        "location__country",
        "location__street",
    ]
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.request.method == "GET":
            return EventRetrieveSerializer
        return EventCreateUpdateSerializer


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    # serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LocationFilter
    search_fields = ["name", "country", "city", "street"]
    ordering_fields = ["name", "longitude", "latitude"]
    pagination_class = DefaultPagination

    # def get_queryset(self):
    #     return Location.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return LocationRetrieveSerializer
        return LocationCreateUpdateSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def destroy(self, request: Request, *args, **kwargs):
        if Event.objects.filter(location_id=kwargs["pk"]).count() > 0:
            return Response(
                {
                    "error": "Location cannot be deleted, because it is associated with an event.",
                },
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)


# * should I display an events in location? or it's better to add nested location to an event
# * how to integrate with a 'map' service to set a location
