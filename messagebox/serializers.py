from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Message, MessageThread

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "receiver",
            "content",
            "date_sent",
            "read_status",
            "thread",
        ]

    def validate(self, attrs: dict) -> dict:
        instance = Message(**attrs)
        instance.clean()
        return attrs


class MessageContentUpdateSerializer(serializers.ModelSerializer):
    """Limits editable fields to content only."""

    class Meta:
        model = Message
        fields = ["id", "content", "sender", "receiver"]
        read_only_fields = ["id", "receiver", "sender"]


class MessageThreadSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True
    )
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = MessageThread
        fields = ["id", "name", "participants", "messages", "created_at"]


class MessageThreadParticipantsUpdateSerializer(serializers.ModelSerializer):
    """Limits editable fields to participants only."""

    participants = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True
    )

    class Meta:
        model = MessageThread
        fields = ["participants"]
