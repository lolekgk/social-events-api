from django.db.models import Q
from django_filters.rest_framework import CharFilter, FilterSet

from .models import Message


class MessageFilter(FilterSet):
    msg_direction = CharFilter(method="filter_message_direction")

    class Meta:
        model = Message
        fields = ["msg_direction"]

    def filter_message_direction(self, queryset, name, value):
        user = self.request.user
        sent_filter = Q(sender=user, deleted_by_sender=False)
        received_filter = Q(receiver=user, deleted_by_receiver=False)
        filter_conditions = {
            "sent": queryset.filter(sent_filter),
            "received": queryset.filter(received_filter),
        }
        return filter_conditions.get(
            value, queryset.filter(sent_filter | received_filter)
        )
