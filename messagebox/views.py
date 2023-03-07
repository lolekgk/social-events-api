from django.db.models import Max
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

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
        - msg_direction: sent, received (default: received)


    POST: create and send a private/thread message.
    """

    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated, MessageSenderReceiverPermission]
    pagination_class = DefaultPagination

    def perform_create(self, serializer: MessageSerializer):
        serializer.save(sender=self.request.user)

    def get_queryset(self):
        message_direction = self.request.query_params.get(
            "msg_direction", "received"
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


class MessageDetailView(RetrieveDestroyAPIView):
    """
    GET: retrieve user's message details.

    DELETE: mark current user's message as deleted.

    """

    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    permission_classes = [IsAuthenticated, MessageSenderReceiverPermission]

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance: Message = self.get_object()
        is_sender = request.user == instance.sender
        is_receiver = request.user == instance.receiver
        is_deleted_by_sender = instance.deleted_by_sender and is_sender
        is_deleted_by_receiver = instance.deleted_by_receiver and is_receiver

        if is_deleted_by_receiver or is_deleted_by_sender:
            return Response(
                data={"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if is_receiver and not instance.read_status:
            instance.read_status = True
            instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_destroy(self, instance: Message):
        if instance.sender == self.request.user:
            instance.deleted_by_sender = True
        else:
            instance.deleted_by_receiver = True
        instance.save()


class MessageThreadListView(ListCreateAPIView):
    """
    GET: retrieve a list of current user's message threads.

    POST: create a new message thread with current user and selected user's.
    """

    serializer_class = MessageThreadSerializer
    queryset = MessageThread.objects.all()
    permission_classes = [IsAuthenticated, MessageThreadParticipantPermission]

    def perform_create(self, serializer: MessageThreadSerializer):
        serializer.save(participants=[self.request.user])

    def get_queryset(self):
        return self.request.user.message_threads.all()


class MessageThreadDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET: retrieve a message thread details.

    PUT: update participants of the message thread.

    DELETE:
    """

    serializer_class = MessageThreadSerializer
    queryset = MessageThread.objects.all()
    permission_classes = [IsAuthenticated, MessageThreadParticipantPermission]
