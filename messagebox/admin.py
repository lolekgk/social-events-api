from django.contrib import admin

from .models import Message, MessageThread


class MessageInline(admin.StackedInline):
    model = Message
    extra = 0


# TODO make it more like users admin -> more features
# after clicking on sender/receiver go to the related user profile
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "content",
        "sender",
        "receiver",
        "thread_id",
        "date_sent",
        "read_status",
    ]
    list_filter = ["sender", "receiver"]
    search_fields = ["sender__username", "receiver__username"]

    def thread_id(self, obj: Message) -> int | None:
        if obj.thread:
            return obj.thread.id
        return None


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ["id", "participants_list", "created_at"]
    search_fields = ["participants__username"]
    inlines = [MessageInline]

    def participants_list(self, obj: MessageThread) -> str:
        return ", ".join([p.username for p in obj.participants.all()])

    participants_list.short_description = "Participants"
