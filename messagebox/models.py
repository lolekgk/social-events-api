from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


# TODO add archived by participant in a future (if someone sends a new message thread will appear again)
class MessageThread(models.Model):
    name = models.CharField(max_length=50)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="message_threads"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_by_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="deleted_message_threads",
        blank=True,
    )

    def __str__(self) -> str:
        return self.name


# TODO add read_by for thread message for each participant in the future
class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="messages_sent",
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
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
    deleted_by_receiver = models.BooleanField(
        default=None, null=True, blank=True
    )

    def __str__(self) -> str:
        if self.receiver is None:
            return f"{self.sender.username} broadcasts: {self.content}"
        return f"{self.sender.username} to {self.receiver.username}: {self.content}"

    def save(self, *args, **kwargs) -> None:
        if self.thread is None:
            self.deleted_by_receiver = False
        super().save(*args, **kwargs)

    def clean(self) -> None:
        if self.thread is None and self.receiver is None:
            raise ValidationError(
                "Either the 'thread' or 'receiver' field must be set."
            )
        if self.thread is not None and self.receiver is not None:
            raise ValidationError(
                "Only one of 'thread' or 'receiver' fields can be set."
            )
        if self.thread is not None and self.deleted_by_receiver is not None:
            raise ValidationError(
                "The 'deleted_by_receiver' field cannot be set when a 'thread' is present."
            )

    class Meta:
        ordering = ["-date_sent"]
        constraints = [
            models.CheckConstraint(
                check=(
                    Q(thread__isnull=False) & Q(receiver__isnull=True)
                    | Q(thread__isnull=True) & Q(receiver__isnull=False)
                ),
                name="thread_or_receiver_set",
            ),
            models.CheckConstraint(
                check=(
                    Q(thread__isnull=True)
                    | Q(deleted_by_receiver__isnull=True)
                ),
                name="deleted_by_receiver_null_when_thread_present",
            ),
        ]
