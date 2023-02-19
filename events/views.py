from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import LocationFilter
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
    filter_backends = [OrderingFilter]
    ordering_fields = ['name']
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return EventRetrieveSerializer
        return EventCreateUpdateSerializer


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    # serializer_class = LocationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = LocationFilter
    search_fields = ['name', 'country', 'city', 'street']
    ordering_fields = ['name', 'longitude', 'latitude']
    pagination_class = DefaultPagination

    # def get_queryset(self):
    #     return Location.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LocationRetrieveSerializer
        return LocationCreateUpdateSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request: Request, *args, **kwargs):
        if Event.objects.filter(location_id=kwargs['pk']).count() > 0:
            return Response(
                {
                    "error": "Location cannot be deleted, because it is associated with an event.",
                },
                status=status.HTTP_409_CONFLICT,
            )
        return super().destroy(request, *args, **kwargs)
