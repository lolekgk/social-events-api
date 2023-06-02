import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from model_bakery import baker

from messagebox.models import Message, MessageThread

User = get_user_model()


@pytest.fixture
def test_private_message(test_sender):
    receiver = baker.make(User, username="test_receiver")

    msg = baker.make(
        Message,
        thread=None,
        sender=test_sender,
        receiver=receiver,
        content="test_message",
    )
    yield msg
    del msg


@pytest.fixture
def test_thread():
    thread = baker.make(MessageThread, name="test_thread")
    yield thread
    del thread


@pytest.mark.django_db
class TestMessageModel:
    def test_init_magic_method_without_thread(self, test_private_message):
        assert test_private_message.deleted_by_receiver is False

    def test_init_magic_method_with_thread(self, test_sender):
        thread_participants = baker.make(User, _quantity=5)
        thread_participants.append(test_sender)

        thread = baker.make(MessageThread, participants=thread_participants)
        message = baker.make(Message, thread=thread, sender=test_sender)

        assert message.deleted_by_receiver is None

    def test_str_method_with_receiver(self, test_private_message):
        assert (
            str(test_private_message)
            == "test_sender to test_receiver: test_message"
        )

    def test_str_method_without_receiver(self, test_private_message):
        test_private_message.receiver = None

        assert (
            str(test_private_message) == "test_sender broadcasts: test_message"
        )

    def test_save(self, test_sender):
        thread_participants = baker.make(User, _quantity=5)
        # sender is not a thread participant
        thread = baker.make(MessageThread, participants=thread_participants)
        message = Message(thread=thread, sender=test_sender)

        with pytest.raises(
            ValidationError,
            match="Only a thread participant can send a thread message.",
        ):
            message.save()

    def test_clean_thread_and_receiver_are_both_none(self):
        message = Message(thread=None, receiver=None)

        with pytest.raises(
            ValidationError,
            match="Either the 'thread' or 'receiver' field must be set.",
        ):
            message.clean()

    def test_clean_thread_and_receiver_are_both_set(self):
        receiver = baker.make(User)
        thread = baker.make(MessageThread)

        message = Message(thread=thread, receiver=receiver)

        with pytest.raises(
            ValidationError,
            match="Only one of 'thread' or 'receiver' fields can be set.",
        ):
            message.clean()

    def test_clean_thread_and_deleted_by_receiver_both_set(self):
        thread = baker.make(MessageThread)
        message = Message(thread=thread, deleted_by_receiver=True)

        with pytest.raises(
            ValidationError,
            match="The 'deleted_by_receiver' field cannot be set when a 'thread' is present.",
        ):
            message.clean()

    def test_perform_soft_delete_user_is_not_a_sender(
        self, test_private_message
    ):
        user = baker.make(User)

        test_private_message.perform_soft_delete(user=user)

        assert test_private_message.deleted_by_receiver is True
        assert test_private_message.deleted_by_sender is False

    def test_perform_soft_delete_user_is_a_sender(
        self, test_private_message, test_sender
    ):
        test_private_message.perform_soft_delete(user=test_sender)

        assert test_private_message.deleted_by_sender is True
        assert test_private_message.deleted_by_receiver is False


@pytest.mark.django_db
class TestMessageThreadModel:
    def test_str_method(self, test_thread):
        assert str(test_thread) == "test_thread"

    def test_perform_soft_delete(self, test_thread):
        user = baker.make(User)
        test_thread.perform_soft_delete(user=user)

        assert user in test_thread.deleted_by_users.all()
