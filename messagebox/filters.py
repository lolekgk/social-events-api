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
        if value == "sent":
            return queryset.filter(sender=user, deleted_by_sender=False)
        elif value == "received":
            return queryset.filter(receiver=user, deleted_by_receiver=False)
        return queryset.filter(
            Q(sender=user, deleted_by_sender=False)
            | Q(receiver=user, deleted_by_receiver=False)
        )
