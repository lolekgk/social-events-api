import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker

from messagebox.models import Message, MessageThread

User = get_user_model()


@pytest.mark.django_db
class TestMessageModel:
    def test_init_magic_method_without_thread(self):
        receiver = baker.make(User, pk=1)
        sender = baker.make(User, pk=2)
        message = baker.make(
            Message, thread=None, sender=sender, receiver=receiver
        )

        assert message.deleted_by_receiver is False

    def test_init_magic_method_with_thread(self):
        sender = baker.make(User)
        thread_participants = baker.make(User, _quantity=5)
        thread_participants.append(sender)
        thread = baker.make(MessageThread, participants=thread_participants)
        message = baker.make(Message, thread=thread, sender=sender)

        assert message.deleted_by_receiver is None
