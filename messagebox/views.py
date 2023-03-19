from django.db.models import Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

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
    """GET (list): Retrieve a list of the current user's messages(excluding deleted messages).

    Query Parameters:
        - msg_direction: sent, received (default: received)

    GET (retrieve): Retrieve the details of a specific user's message.

    POST: Create and send a private/thread message.

    PUT: Update the content of a message. Can only be done by the message sender.
        Note: This action replaces the entire message object with the new data.

    PATCH: Partially update the content of a message. Can only be done by the message sender.
        Note: This action updates only the fields provided in the request data.

    DELETE: Mark a message as deleted for the current user.

    Additional Filters:
        - content, receiver__username for search_fields
        - date_sent for ordering_fields
    """

    queryset = Message.objects.all()
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ["content", "receiver__username"]
    ordering_fields = ["date_sent"]

    def get_permissions(self):
        permission_classes = [IsAuthenticated, MessageSenderReceiverPermission]
        if self.request.method in ["PUT", "PATCH"]:
            permission_classes.append(MessageUpdatePermission)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return MessageContentUpdateSerializer
        return MessageSerializer

    def perform_create(self, serializer: MessageSerializer):
        # Ensure, that only a thread participant can send a thread message
        thread = serializer.validated_data.get("thread")
        if thread and self.request.user not in thread.participants.all():
            raise ValidationError(
                "Only a thread participant can send a thread message."
            )
        serializer.save(sender=self.request.user)

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


# TODO check if no participant can add a thread message
# jesli uzytknownik nie jest w thread participants nie moze wyslac wiadomosci
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
    ):
        filtered_messages = Message.objects.exclude(
            sender=self.request.user, deleted_by_sender=True
        )
        return self.queryset.filter(
            participants=self.request.user
        ).prefetch_related(Prefetch("messages", queryset=filtered_messages))


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
