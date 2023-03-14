from django.db.models import Q
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
        message_direction_filters = {  # TODO fixed
            "sent": self.queryset.filter(
                sender=self.request.user, deleted_by_sender=False
            ),
            "received": self.queryset.filter(
                receiver=self.request.user, deleted_by_receiver=False
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

    def get_queryset(self):
        return self.queryset.filter(
            Q(sender=self.request.user, deleted_by_sender=False)
            | Q(receiver=self.request.user, deleted_by_receiver=False)
        )

    def get_object(self) -> Message:
        message: Message = super().get_object()
        if self.request.user == message.receiver and not message.read_status:
            message.read_status = True
            message.save()
        return message

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
        participants = serializer.validated_data.get("participants", [])
        participants.append(self.request.user)
        serializer.save(participants=participants)

    def get_queryset(
        self,
    ):  # TODO filter deleted_by_sender msg if user is sender
        queryset = self.request.user.message_threads.all()
        return queryset


# TODO
class MessageThreadDetailView(RetrieveUpdateDestroyAPIView):
    """
    GET: retrieve a message thread details.

    PUT: update participants of the message thread.

    DELETE: delete entire message thread
    """

    serializer_class = MessageThreadSerializer
    queryset = MessageThread.objects.all()
    permission_classes = [IsAuthenticated, MessageThreadParticipantPermission]

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        instance: MessageThread = self.get_object()

        for message in instance.messages.all():
            if message.read_status is False:
                message.read_status = True
                message.save()
            instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
