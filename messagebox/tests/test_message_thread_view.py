import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from messagebox.models import Message, MessageThread

User = get_user_model()


@pytest.fixture
def create_threads(test_sender):
    participants_set = baker.prepare(User, _quantity=5)
    participants_set.append(test_sender)
    threads = baker.make(
        MessageThread,
        participants=participants_set,
        _quantity=10,
    )
    yield threads
    del threads


@pytest.fixture
def thread_with_messages(test_sender):
    participants_set = baker.prepare(User, _quantity=5)
    participants_set.append(test_sender)
    thread = baker.make(MessageThread, participants=participants_set)
    baker.make(
        Message, thread=thread, sender=test_sender, receiver=None, _quantity=25
    )
    yield thread
    del thread


@pytest.fixture
def create_thread_with_deleted_messages(test_sender):
    participants_set = baker.prepare(User, _quantity=5)
    participants_set.append(test_sender)
    thread = baker.make(MessageThread, participants=participants_set)
    baker.make(
        Message, thread=thread, sender=test_sender, receiver=None, _quantity=5
    )
    baker.make(
        Message,
        thread=thread,
        sender=test_sender,
        deleted_by_sender=True,
        receiver=None,
        _quantity=5,
    )
    yield thread
    del thread


@pytest.fixture
def create_deleted_thread(test_sender):
    participants_set = baker.prepare(User, _quantity=5)
    participants_set.append(test_sender)
    thread = baker.make(
        MessageThread,
        participants=participants_set,
        deleted_by_users=participants_set,
    )
    yield thread
    del thread


@pytest.fixture
def thread_payload():
    payload = {"name": "test", "participants": []}
    yield payload
    del payload


@pytest.fixture
def update_thread_payload(test_sender):
    new_participant = baker.make(User)
    payload = {
        "name": "updated_test",
        "participants": [new_participant.pk, test_sender.pk],
    }
    yield payload
    del payload


@pytest.fixture
def not_participant():
    user = baker.make(User)
    yield user
    del user


@pytest.mark.django_db
class TestListMessageThread:
    def test_get_threads_as_participant(
        self,
        api_client: APIClient,
        create_threads,  # quantity = 10
        thread_with_messages,  # quantity = 1, messages quantity = 25
        test_sender,
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.get("/messagebox/threads/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 11

        results = response.json().get("results")
        # check number of messages in last thread
        assert len(results[-1].get("messages")) == 25

    def test_get_threads_as_participant_with_deleted_thread(
        self,
        api_client: APIClient,
        create_deleted_thread,
        test_sender,
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.get("/messagebox/threads/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_get_threads_as_participant_with_deleted_thread_messages(
        self,
        api_client: APIClient,
        create_thread_with_deleted_messages,  # quantity = 1, messages = 10, without deleted = 5
        test_sender,
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.get("/messagebox/threads/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

        results = response.json().get("results")
        # check number of messages in a thread (deleted ones are not counted)
        assert len(results[-1].get("messages")) == 5

    def test_get_threads_as_anonymous_user(
        self,
        api_client: APIClient,
        create_threads,  # quantity = 10
    ) -> None:
        response = api_client.get("/messagebox/threads/", format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_threads_as_not_a_participant(
        self,
        api_client: APIClient,
        create_threads,  # quantity = 10
        not_participant,
    ) -> None:
        api_client.force_authenticate(not_participant)

        response = api_client.get("/messagebox/threads/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0


@pytest.mark.django_db
class TestRetrieveMessageThread:
    def test_get_thread_as_anonymous_user(
        self, api_client: APIClient, thread_with_messages
    ) -> None:
        response = api_client.get(
            f"/messagebox/threads/{thread_with_messages.pk}/",
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_thread_as_not_participant(
        self,
        api_client: APIClient,
        thread_with_messages,
        not_participant,
    ) -> None:
        api_client.force_authenticate(not_participant)

        response = api_client.get(
            f"/messagebox/threads/{thread_with_messages.pk}/",
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_thread_as_participant(
        self,
        api_client: APIClient,
        thread_with_messages,  # quantity = 1, messages quantity = 25
        test_sender,
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.get(
            f"/messagebox/threads/{thread_with_messages.pk}/",
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == thread_with_messages.name
        assert len(response.data["messages"]) == 25

    def test_get_non_existing_thread(
        self,
        api_client: APIClient,
        test_sender,
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.get(
            "/messagebox/threads/1/",
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCreateMessageThread:
    def test_create_thread_as_anonymous_user(
        self, api_client: APIClient, thread_payload
    ) -> None:
        response = api_client.post(
            "/messagebox/threads/",
            data=thread_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_thread_with_invalid_data_no_name(
        self, api_client: APIClient, test_sender
    ) -> None:
        api_client.force_authenticate(test_sender)
        invalid_payload = {"name": "", "participants": []}

        response = api_client.post(
            "/messagebox/threads/",
            data=invalid_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_thread_with_invalid_data_non_exising_participants(
        self, api_client: APIClient, test_sender
    ) -> None:
        api_client.force_authenticate(test_sender)
        invalid_payload = {"name": "test", "participants": [99, 109]}

        response = api_client.post(
            "/messagebox/threads/",
            data=invalid_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_thread_with_invalid_data_not_active_participants(
        self, api_client: APIClient, test_sender
    ) -> None:
        api_client.force_authenticate(test_sender)
        not_active_users_ids = [
            user.pk for user in baker.make(User, is_active=False, _quantity=10)
        ]
        invalid_payload = {
            "name": "test",
            "participants": not_active_users_ids,
        }

        response = api_client.post(
            "/messagebox/threads/",
            data=invalid_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_thread_with_valid_data_and_user(
        self, api_client: APIClient, test_sender, thread_payload
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.post(
            "/messagebox/threads/",
            data=thread_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        thread = MessageThread.objects.get(id=response.data["id"])

        assert thread is not None
        assert test_sender in thread.participants.all()
        assert thread.name == thread_payload["name"]


@pytest.mark.django_db
class TestUpdateMessageThread:
    def test_update_thread_as_participant_valid_data(
        self,
        api_client: APIClient,
        test_sender,
        thread_with_messages,
        update_thread_payload,  # 2 participants
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.put(
            path=f"/messagebox/threads/{thread_with_messages.pk}/",
            data=update_thread_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        updated_thread = MessageThread.objects.get(id=response.data["id"])

        assert test_sender in updated_thread.participants.all()
        assert updated_thread.participants.count() == 2
        assert updated_thread.name == "updated_test"

    def test_update_thread_as_participant_without_participants(
        self,
        api_client: APIClient,
        test_sender,
        thread_with_messages,
        update_thread_payload,
    ) -> None:
        api_client.force_authenticate(test_sender)
        update_thread_payload["participants"].clear()

        response = api_client.put(
            path=f"/messagebox/threads/{thread_with_messages.pk}/",
            data=update_thread_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        updated_thread = MessageThread.objects.get(id=response.data["id"])

        assert test_sender not in updated_thread.participants.all()
        assert updated_thread.participants.count() == 0
        assert updated_thread.name == "updated_test"

    def test_update_non_existing_thread(
        self, api_client: APIClient, test_sender, update_thread_payload
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.put(
            path="/messagebox/threads/1/",
            data=update_thread_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_thread_as_anonymous_user(
        self,
        api_client: APIClient,
        update_thread_payload,
        thread_with_messages,
    ) -> None:
        response = api_client.put(
            path=f"/messagebox/threads/{thread_with_messages.pk}/",
            data=update_thread_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_thread_as_not_a_participant(
        self,
        api_client: APIClient,
        update_thread_payload,
        thread_with_messages,
        not_participant,
    ) -> None:
        api_client.force_authenticate(not_participant)

        response = api_client.put(
            path=f"/messagebox/threads/{thread_with_messages.pk}/",
            data=update_thread_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_partial_thread_data(
        self,
        api_client: APIClient,
        test_sender,
        thread_with_messages,
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.patch(
            path=f"/messagebox/threads/{thread_with_messages.pk}/",
            data={"name": "updated_name"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        updated_thread = MessageThread.objects.get(id=response.data["id"])

        assert updated_thread.name == "updated_name"


@pytest.mark.django_db
class TestDeleteMessageThread:
    def test_delete_message_as_anonymous_user(
        self, api_client: APIClient, thread_with_messages
    ) -> None:
        response = api_client.delete(
            path=f"/messagebox/threads/{thread_with_messages.pk}/",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_message_as_participant(
        self, api_client: APIClient, thread_with_messages, test_sender
    ) -> None:
        api_client.force_authenticate(test_sender)

        response = api_client.delete(
            path=f"/messagebox/threads/{thread_with_messages.pk}/",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        thread_with_messages.refresh_from_db()

        assert test_sender in thread_with_messages.deleted_by_users.all()

    def test_delete_message_as_not_participant(
        self, api_client: APIClient, thread_with_messages, not_participant
    ) -> None:
        api_client.force_authenticate(not_participant)

        response = api_client.delete(
            path=f"/messagebox/threads/{thread_with_messages.pk}/",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
