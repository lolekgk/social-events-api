import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from messagebox.models import Message

User = get_user_model()


@pytest.fixture
def create_messages(test_receiver, test_sender):
    messages = baker.make(
        Message,
        sender=test_sender,
        receiver=test_receiver,
        thread=None,
        _quantity=10,
    )
    yield messages
    del messages


@pytest.fixture
def message(test_receiver, test_sender):
    msg = baker.make(
        Message,
        sender=test_sender,
        receiver=test_receiver,
        thread=None,
    )
    yield msg
    del msg


@pytest.fixture
def messages_deleted_by_receiver(test_receiver, test_sender):
    messages = baker.make(
        Message,
        sender=test_sender,
        receiver=test_receiver,
        deleted_by_receiver=True,
        thread=None,
        _quantity=10,
    )
    yield messages
    del messages


@pytest.fixture
def messages_deleted_by_sender(test_receiver, test_sender):
    messages = baker.make(
        Message,
        sender=test_sender,
        receiver=test_receiver,
        deleted_by_sender=True,
        thread=None,
        _quantity=10,
    )
    yield messages
    del messages


@pytest.fixture
def message_payload(test_receiver):
    payload = {
        "receiver": test_receiver.pk,
        "content": "test_content",
    }
    yield payload
    del payload


@pytest.fixture
def update_message_payload(test_receiver, test_sender):
    payload = {
        "sender": test_sender.pk,
        "receiver": test_receiver.pk,
        "content": "updated_content",
    }
    yield payload
    del payload


@pytest.mark.django_db
class TestListMessage:
    def test_get_all_messages_as_sender(
        self, api_client: APIClient, create_messages, test_sender
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.get("/messagebox/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 10

    def test_get_sent_messages_as_sender(
        self, api_client: APIClient, create_messages, test_sender
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.get(
            "/messagebox/?msg_direction=sent", format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 10

    def test_get_received_messages_as_sender(
        self, api_client: APIClient, create_messages, test_sender
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.get(
            "/messagebox/?msg_direction=received", format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_get_messages_as_receiver(
        self, api_client: APIClient, create_messages, test_receiver
    ) -> None:
        api_client.force_authenticate(test_receiver)

        response = api_client.get("/messagebox/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 10

    def test_get_messages_as_receiver_with_deleted_messages_by_receiver(
        self,
        api_client: APIClient,
        create_messages,
        messages_deleted_by_receiver,
        test_receiver,
    ) -> None:
        api_client.force_authenticate(test_receiver)

        response = api_client.get("/messagebox/", format="json")

        assert response.status_code == status.HTTP_200_OK
        # without filtering deleted messeges count would be equal to 20
        assert response.data["count"] == 10

    def test_get_messages_as_receiver_with_deleted_messages_by_sender(
        self,
        api_client: APIClient,
        create_messages,
        messages_deleted_by_sender,
        test_receiver,
    ) -> None:
        api_client.force_authenticate(test_receiver)

        response = api_client.get("/messagebox/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 20

    def test_get_messages_as_sender_with_deleted_messages_by_sender(
        self,
        api_client: APIClient,
        create_messages,
        messages_deleted_by_sender,
        test_sender,
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.get("/messagebox/", format="json")

        assert response.status_code == status.HTTP_200_OK
        # without filtering deleted messeges count would be equal to 20
        assert response.data["count"] == 10

    def test_get_messages_as_sender_with_deleted_messages_by_receiver(
        self,
        api_client: APIClient,
        create_messages,
        messages_deleted_by_receiver,
        test_sender,
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.get("/messagebox/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 20

    def test_get_messages_as_anonymous_user(
        self, api_client: APIClient
    ) -> None:
        response = api_client.get("/messagebox/", format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_messages_as_other_user(  # not a sender/receiver
        self, api_client: APIClient, create_messages
    ) -> None:
        other_user = baker.make(User, username="other_user")
        api_client.force_authenticate(other_user)

        response = api_client.get("/messagebox/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0


@pytest.mark.django_db
class TestRetrieveMessage:
    def test_get_message_as_sender(
        self, api_client: APIClient, message, test_sender
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.get(f"/messagebox/{message.pk}/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["content"] == message.content
        assert response.data["read_status"] is False

    def test_get_message_as_receiver(
        self, api_client: APIClient, message, test_receiver
    ) -> None:
        api_client.force_authenticate(test_receiver)

        response = api_client.get(f"/messagebox/{message.pk}/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["content"] == message.content
        assert response.data["read_status"] is True

    def test_get_message_as_other_user(
        self, api_client: APIClient, message
    ) -> None:
        other_user = baker.make(User)
        api_client.force_authenticate(other_user)

        response = api_client.get(f"/messagebox/{message.pk}/", format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_message_as_anonymous_user(
        self, api_client: APIClient, message
    ) -> None:
        response = api_client.get(f"/messagebox/{message.pk}/", format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_non_existing_message(
        self, api_client: APIClient, test_sender
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.get("/messagebox/1/", format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCreateMessage:
    def test_create_message_as_anonymous_user(
        self, api_client: APIClient, message_payload
    ) -> None:
        response = api_client.post(
            path="/messagebox/", data=message_payload, format="json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_message_with_invalid_data_no_content(
        self,
        api_client: APIClient,
        test_sender,
        test_receiver,
    ) -> None:
        api_client.force_authenticate(test_sender)

        invalid_payload = {
            "sender": test_sender.pk,
            "receiver": test_receiver.pk,
            "content": "",
        }
        response = api_client.post(
            path="/messagebox/", data=invalid_payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_message_with_invalid_data_not_existing_receiver(
        self,
        api_client: APIClient,
        test_sender,
    ) -> None:
        api_client.force_authenticate(test_sender)

        invalid_payload = {
            "sender": test_sender.pk,
            "receiver": 999999,
            "content": "test_content",
        }
        response = api_client.post(
            path="/messagebox/", data=invalid_payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_message_with_invalid_data_not_active_receiver(
        self, api_client: APIClient, test_sender
    ) -> None:
        api_client.force_authenticate(test_sender)
        not_active_user = baker.make(User, is_active=False)

        invalid_payload = {
            "sender": test_sender.pk,
            "receiver": not_active_user.pk,
            "content": "test_content",
        }
        response = api_client.post(
            path="/messagebox/", data=invalid_payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_message_valid_data_and_user(
        self,
        api_client: APIClient,
        test_sender,
        test_receiver,
        message_payload,
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.post(
            path="/messagebox/", data=message_payload, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED

        message = Message.objects.get(id=response.data["id"])

        assert message is not None
        assert message.sender == test_sender
        assert message.receiver == test_receiver
        assert message.content == message_payload["content"]


@pytest.mark.django_db
class TestUpdateMessage:
    def test_update_message_as_sender_valid_data(
        self,
        api_client: APIClient,
        test_sender,
        test_receiver,
        message,
        update_message_payload,
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.put(
            path=f"/messagebox/{message.pk}/",
            data=update_message_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        updated_message = Message.objects.get(id=response.data["id"])

        assert updated_message.content == "updated_content"
        assert updated_message.sender == test_sender
        assert updated_message.receiver == test_receiver

    def test_update_message_as_sender_with_changed_receiver(
        self,
        api_client: APIClient,
        test_sender,
        test_receiver,
        message,
        update_message_payload,
    ) -> None:
        api_client.force_authenticate(test_sender)
        update_message_payload["receiver"] = 99

        response = api_client.put(
            path=f"/messagebox/{message.pk}/",
            data=update_message_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        updated_message = Message.objects.get(id=response.data["id"])

        assert updated_message.content == "updated_content"
        assert updated_message.sender == test_sender
        assert updated_message.receiver == test_receiver

    def test_update_message_as_sender_with_changed_sender(
        self,
        api_client: APIClient,
        test_sender,
        test_receiver,
        message,
        update_message_payload,
    ) -> None:
        api_client.force_authenticate(test_sender)
        update_message_payload["sender"] = 99

        response = api_client.put(
            path=f"/messagebox/{message.pk}/",
            data=update_message_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        updated_message = Message.objects.get(id=response.data["id"])

        assert updated_message.content == "updated_content"
        assert updated_message.sender == test_sender
        assert updated_message.receiver == test_receiver

    def test_update_non_existing_message(
        self,
        api_client: APIClient,
        test_sender,
        update_message_payload,
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.put(
            path="/messagebox/1/",
            data=update_message_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_message_as_anonymous_user(
        self, api_client: APIClient, update_message_payload, message
    ) -> None:
        response = api_client.put(
            path=f"/messagebox/{message.pk}/",
            data=update_message_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_message_as_receiver(
        self,
        api_client: APIClient,
        update_message_payload,
        message,
        test_receiver,
    ) -> None:
        api_client.force_authenticate(test_receiver)

        response = api_client.put(
            path=f"/messagebox/{message.pk}/",
            data=update_message_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_partial_message_data(
        self,
        api_client: APIClient,
        test_sender,
        test_receiver,
        message,
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.patch(
            path=f"/messagebox/{message.pk}/",
            data={"content": "updated_content"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        updated_message = Message.objects.get(id=response.data["id"])

        assert updated_message.content == "updated_content"
        assert updated_message.sender == test_sender
        assert updated_message.receiver == test_receiver


@pytest.mark.django_db
class TestDeleteMessage:
    def test_delete_message_as_anonymous_user(
        self, api_client: APIClient, message
    ) -> None:
        response = api_client.delete(
            path=f"/messagebox/{message.pk}/", format="json"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_message_as_sender(
        self, api_client: APIClient, message, test_sender
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.delete(
            path=f"/messagebox/{message.pk}/", format="json"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        message.refresh_from_db()

        assert message.deleted_by_sender is True
        assert message.deleted_by_receiver is False

    def test_delete_message_as_receiver(
        self, api_client: APIClient, message, test_receiver
    ) -> None:
        api_client.force_authenticate(test_receiver)

        response = api_client.delete(
            path=f"/messagebox/{message.pk}/", format="json"
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        message.refresh_from_db()

        assert message.deleted_by_sender is False
        assert message.deleted_by_receiver is True
