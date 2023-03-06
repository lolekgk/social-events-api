from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import Message, MessageThread


class MessageSenderReceiverPermission(BasePermission):
    """Sets the message access limitation to sender and receiver"""

    def has_object_permission(
        self, request: Request, view: APIView, obj: Message
    ) -> bool:
        if (obj.sender == request.user) or (obj.sender == request.user):
            return True
        return False


class MessageThreadParticipantPermission(BasePermission):
    """Sets the message thread access to thread participants only"""

    def has_object_permission(
        self, request: Request, view: APIView, obj: MessageThread
    ) -> bool:
        if request.user in obj.participants.all():
            return True
        return False
