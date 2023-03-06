from rest_framework.generics import ListCreateAPIView

from .models import Message, MessageThread
from .pagination import DefaultPagination
from .permissions import (
    MessageSenderReceiverPermission,
    MessageThreadParticipantPermission,
)
from .serializers import MessageSerializer, MessageThreadSerializer


class MessageListView(ListCreateAPIView):
    """
    GET: retrieve a list of current user's messages(deleted messages are ommited).
        query parameters:
        - message_direction: sent, received (default: received)


    POST: create and send a message.
    """

    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    pagination_class = DefaultPagination

    def perform_create(self, serializer: MessageSerializer):
        serializer.save(sender=self.request.user)

    def get_queryset(self):
        message_direction = self.request.query_params.get(
            "message_direction", "received"
        )
        message_direction_filters = {
            "sent": self.request.user.messages_sent.filter(
                deleted_by_sender=False
            ),
            "received": self.request.user.messages_received.filter(
                deleted_by_receiver=False
            ),
        }
        return message_direction_filters[message_direction]
