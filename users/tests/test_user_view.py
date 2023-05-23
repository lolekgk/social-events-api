import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User


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
        user = baker.make(User, pk=1)

        response = api_client.get(f"/users/{user.pk}/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("email") is None

    def test_get_user_own_profile(self, api_client: APIClient) -> None:
        user = baker.make(User, pk=1)
        api_client.force_authenticate(user)

        response = api_client.get(f"/users/{user.pk}/", format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("email") is not None

    def test_get_non_existing_user(self, api_client: APIClient) -> None:

        response = api_client.get("/users/1/", format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeleteUser:
    def test_delete_user_as_anonymous_user(
        self, api_client: APIClient
    ) -> None:
        user = baker.make(User, pk=1)

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
        user = baker.make(User, pk=1)
        api_client.force_authenticate(user)

        response = api_client.delete(f"/users/{user.pk}/", format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
