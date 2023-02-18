from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from events.models import Event, Location
from events.serializers import LocationSerializer


class LocationViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request: Request, *args, **kwargs):
        if Event.objects.filter(location_id=kwargs['pk']).count() > 0:
            return Response(
                {
                    "error": "Location cannot be deleted, because it is associated with an event.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
