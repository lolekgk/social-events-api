from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from events.models import Event, Location
from events.pagination import DefaultPagination
from events.serializers import LocationSerializer


class EventViewSet(ModelViewSet):
    pass


class EventOrganizerListView:
    pass


class EventOrganizerDetailVew:
    pass


class EventParticipantListView:
    pass


class EventParticipantDetailView:
    pass


class EventInvitationListView:
    pass


class EventIvitationDetailView:
    pass


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'country', 'city', 'street']
    ordering_fields = ['name', 'longitude', 'latitude']
    pagination_class = DefaultPagination

    # def get_queryset(self):
    #     return Location.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request: Request, *args, **kwargs):
        if Event.objects.filter(location_id=kwargs['pk']).count() > 0:
            return Response(
                {
                    "error": "Location cannot be deleted, because it is associated with an event.",
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().destroy(request, *args, **kwargs)
