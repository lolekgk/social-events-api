from django.db.models import Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer

from .filters import MessageFilter
from .models import Message, MessageThread
from .pagination import DefaultPagination
from .permissions import (
    MessageSenderReceiverPermission,
    MessageThreadParticipantPermission,
    MessageUpdatePermission,
)
from .serializers import (
    MessageContentUpdateSerializer,
    MessageSerializer,
    MessageThreadParticipantsUpdateSerializer,
    MessageThreadSerializer,
)


class MessageViewSet(viewsets.ModelViewSet):
    """
    GET (list): Retrieve a list of the current user's messages(excluding deleted messages).

    Query Parameters:
        - msg_direction: sent, received (default: received)

    GET (retrieve): Retrieve the details of a specific user's message.

    POST: Create and send a private/thread message.

    PUT: Update the content of a message. It can be done only by the message sender.
        Note: This action replaces the entire message object with the new data.

    PATCH: Partially update the content of a message. It can be done only  by the message sender.
        Note: This action updates only the fields provided in the request data.

    DELETE: Mark a message as deleted for the current user.

    Additional Filters:
        - content, receiver__username for search_fields
        - date_sent for ordering_fields
    """

    pagination_class = DefaultPagination
    permission_classes = [
        IsAuthenticated,
        MessageSenderReceiverPermission,
        MessageUpdatePermission,
    ]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ["content", "receiver__username"]
    ordering_fields = ["date_sent"]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return MessageContentUpdateSerializer
        return MessageSerializer

    def perform_create(self, serializer: BaseSerializer):
        serializer.save(sender=self.request.user)

    def get_queryset(self):
        return Message.objects.filter(
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
        instance.perform_soft_delete(self.request.user)


@extend_schema(tags=["threads"])
class MessageThreadViewSet(viewsets.ModelViewSet):
    """
    GET (retrieve): Retrieve the details of a specific message thread, including it's messages.

    POST: Create a new message thread with the specified participants.

    PUT: Update the participants of a message thread.
        Note: This action replaces the entire participant list with the new data.

    PATCH: Partially update the participants of a message thread.
        Note: This action updates only the fields provided in the request data.

    DELETE: Mark a message thread as deleted for the current user.

    Additional Filters:
        - messages__content, participants__username for search_fields
        - created_at for ordering_fields
    """

    permission_classes = [IsAuthenticated, MessageThreadParticipantPermission]
    pagination_class = DefaultPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["messages__content", "participants__username"]
    ordering_fields = ["created_at"]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return MessageThreadParticipantsUpdateSerializer
        return MessageThreadSerializer

    def perform_create(self, serializer: BaseSerializer):
        participants = serializer.validated_data.get("participants", [])
        participants.append(self.request.user)
        serializer.save(participants=participants)

    def get_queryset(self):
        filtered_messages = Message.objects.exclude(
            sender=self.request.user, deleted_by_sender=True
        )
        return (
            MessageThread.objects.filter(participants=self.request.user)
            .exclude(deleted_by_users=self.request.user)
            .prefetch_related(Prefetch("messages", queryset=filtered_messages))
        )

    def get_object(self) -> MessageThread:
        message_thread: MessageThread = super().get_object()
        message_thread.messages.filter(read_status=False).update(
            read_status=True
        )
        return message_thread

    def perform_destroy(self, instance: MessageThread) -> None:
        instance.perform_soft_delete(self.request.user)
