from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class MessageThread(models.Model):
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="message_threads"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        separator = ", "
        usernames = separator.join(
            [participant.username for participant in self.participants.all()]
        )
        return f"Messages between: {usernames[:-len(separator)]}"


class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name="messages_sent",
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="messages_received",
    )
    thread = models.ForeignKey(
        MessageThread,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    content = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    read_status = models.BooleanField(default=False)
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_receiver = models.BooleanField(default=False)

    def __str__(self) -> str:
        sender_username = getattr(self.sender, "username", "")
        receiver_username = getattr(self.receiver, "username", "")
        if self.receiver is None:
            return f"{sender_username} broadcast: {self.content}"
        return f"{sender_username} to {receiver_username}: {self.content}"

    def clean(self) -> None:
        if self.thread is None and self.receiver is None:
            raise ValidationError(
                "Either the 'thread' or 'receiver' field must be set."
            )
        if self.thread is not None and self.receiver is not None:
            raise ValidationError(
                "Only one of 'thread' or 'receiver' fields can be set."
            )

    class Meta:
        ordering = ["-date_sent"]
