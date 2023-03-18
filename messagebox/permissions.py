from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import Message, MessageThread


class MessageSenderReceiverPermission(permissions.BasePermission):
    """Sets the message access limitation to sender and receiver."""

    def has_object_permission(
        self, request: Request, view: APIView, obj: Message
    ) -> bool:
        if (obj.sender == request.user) or (obj.receiver == request.user):
            return True
        return False


class MessageUpdatePermission(permissions.BasePermission):
    """Only the user who sent a message can update it's content."""

    def has_object_permission(
        self, request: Request, view: APIView, obj: Message
    ) -> bool:
        if request.method in ["PUT", "PATCH"] and obj.sender == request.user:
            return True
        return False


class MessageThreadParticipantPermission(permissions.BasePermission):
    """Sets the message thread access to thread participants only."""

    def has_object_permission(
        self, request: Request, view: APIView, obj: MessageThread
    ) -> bool:
        if request.user in obj.participants.all():
            return True
        return False
