import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User


@pytest.fixture
def user_update_payload_short():
    payload = {
        "first_name": "test",
        "last_name": "test",
    }
    yield payload
    del payload


@pytest.fixture
def user_update_payload():
    friend_one = baker.make(User)
    friend_two = baker.make(User)
    payload = {
        "first_name": "test",
        "last_name": "test",
        "birth_date": "1990-01-01",
        "friends": [friend_one.pk, friend_two.pk],
    }
    yield payload
    del payload


@pytest.mark.django_db
class TestListUser:
    def test_get_users(self, api_client: APIClient) -> None:
        baker.make(User, _quantity=10)

        response = api_client.get("/users/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 10


@pytest.mark.django_db
class TestRetrieveUser:
    def test_get_user_as_anonymous_user(self, api_client: APIClient) -> None:
        user = baker.make(User)

        response = api_client.get(f"/users/{user.pk}/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("email") is None

    def test_get_user_own_profile(self, api_client: APIClient) -> None:
        user = baker.make(User)
        api_client.force_authenticate(user)

        response = api_client.get(f"/users/{user.pk}/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("email") is not None

    def test_get_non_existing_user(self, api_client: APIClient) -> None:

        response = api_client.get("/users/1/", format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUpdateUser:
    def test_update_user_as_anonymous_user(
        self, api_client: APIClient, user_update_payload_short
    ) -> None:
        user = baker.make(User)

        response = api_client.patch(
            f"/users/{user.pk}/", data=user_update_payload_short, format="json"
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_other_user(
        self, api_client: APIClient, user_update_payload_short
    ) -> None:
        current_user = baker.make(User)
        api_client.force_authenticate(current_user)
        user_to_update = baker.make(User)

        response = api_client.patch(
            f"/users/{user_to_update.pk}/",
            data=user_update_payload_short,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_user_own_profile_with_non_existing_friends(
        self, api_client: APIClient, user_update_payload
    ) -> None:
        current_user = baker.make(User)
        api_client.force_authenticate(current_user)
        user_update_payload["friends"] = [9999, 99999]

        response = api_client.put(
            f"/users/{current_user.pk}/",
            data=user_update_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_user_own_profile_short(
        self, api_client: APIClient, user_update_payload_short
    ) -> None:
        user = baker.make(User)
        api_client.force_authenticate(user)

        response = api_client.patch(
            f"/users/{user.pk}/", data=user_update_payload_short, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "test"
        assert response.data["last_name"] == "test"
        assert response.data["email"] == user.email
        assert response.data["username"] == user.username

    def test_update_user_own_profile(
        self, api_client: APIClient, user_update_payload
    ) -> None:
        user = baker.make(User)
        api_client.force_authenticate(user)

        response = api_client.put(
            f"/users/{user.pk}/", data=user_update_payload, format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "test"
        assert response.data["last_name"] == "test"
        assert response.data["email"] == user.email
        assert response.data["username"] == user.username
        assert response.data["birth_date"] == "1990-01-01"
        assert len(response.data["friends"]) == 2


@pytest.mark.django_db
class TestDeleteUser:
    def test_delete_user_as_anonymous_user(
        self, api_client: APIClient
    ) -> None:
        user = baker.make(User)

        response = api_client.delete(f"/users/{user.pk}/", format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_other_user(self, api_client: APIClient) -> None:
        currenct_user = baker.make(User, pk=2)
        api_client.force_authenticate(currenct_user)
        user_to_delete = baker.make(User, pk=1)

        response = api_client.delete(
            f"/users/{user_to_delete.pk}/", format="json"
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_user_own_profile(self, api_client: APIClient) -> None:
        user = baker.make(User)
        api_client.force_authenticate(user)

        response = api_client.delete(f"/users/{user.pk}/", format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
