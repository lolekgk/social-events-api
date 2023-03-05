from django.contrib import admin

from .models import Message, MessageThread


class MessageInline(admin.StackedInline):
    model = Message
    extra = 0


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "content",
        "sender_username",
        "receiver_username",
        "thread",
        "date_sent",
        "read_status",
    ]
    list_filter = ["sender", "receiver"]
    search_fields = ["sender__username", "receiver__username"]

    def sender_username(self, obj: Message) -> str:
        return getattr(obj.sender, "username", "")

    def receiver_username(self, obj: Message) -> str:
        return getattr(obj.receiver, "username", "")


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ["id", "participants_list", "created_at"]
    search_fields = ["participants__username"]
    inlines = [MessageInline]

    def participants_list(self, obj) -> str:
        return ", ".join([p.username for p in obj.participants.all()])

    participants_list.short_description = "Participants"
