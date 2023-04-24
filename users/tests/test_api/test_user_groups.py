from typing import Any

import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from users.models import UserGroup


@pytest.fixture
def create_user_group(api_client: APIClient):
    def do_create_user_group(user_group: dict[str, Any], user_id: int):
        return api_client.post(
            f"/users/{user_id}/groups/", user_group, format="json"
        )

    return do_create_user_group


@pytest.fixture
def retrieve_user_group(api_client: APIClient):
    def do_retrieve_user_group(user_id: int, group_id: int):
        return api_client.get(
            f"/users/{user_id}/groups/{group_id}/", format="json"
        )

    return do_retrieve_user_group


@pytest.mark.django_db
class TestCreateUserGroup:
    def test_create_user_group_as_anonymous_user(
        self, create_user_group
    ) -> None:
        response: Response = create_user_group(
            {"name": "test", "description": "test"}, user_id=1
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_user_group_from_other_users_profile_endpoint(
        self, create_user_group, create_user, authenticate
    ) -> None:
        user = create_user(pk=2)
        authenticate(user)
        other_user_id = 1
        response: Response = create_user_group(
            {"name": "test", "description": "test"}, user_id=other_user_id
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_user_group_with_invalid_data(
        self, create_user_group, create_user, authenticate
    ) -> None:
        user = create_user(pk=1)
        authenticate(user)
        response: Response = create_user_group(
            {
                "name": "",
                "description": "",
                "members": [],
                "administrators": [],
            },
            user_id=user.id,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_group_with_valid_data(
        self, create_user_group, create_user, authenticate
    ) -> None:
        user = create_user(pk=1)
        authenticate(user)
        response: Response = create_user_group(
            {
                "name": "test",
                "description": "test",
                "members": [],
                "administrators": [],
            },
            user_id=user.id,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0
        assert response.data["members"] == [1]
        assert response.data["administrators"] == [1]


@pytest.mark.django_db
class TestRetrieveUserGroup:
    def test_get_existing_user_group(
        self, create_user, authenticate, retrieve_user_group
    ) -> None:
        user = create_user(pk=1)
        authenticate(user)
        user_group = baker.make(
            UserGroup, administrators=[user], members=[user]
        )
        response: Response = retrieve_user_group(user.id, user_group.id)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": user_group.id,
            "name": user_group.name,
            "description": user_group.description,
            "members": [user.id],
            "administrators": [user.id],
        }

    def test_get_non_existing_user_group(
        self, create_user, authenticate, retrieve_user_group
    ) -> None:
        user = create_user(pk=1)
        authenticate(user)
        non_existing_group_id = 2
        response: Response = retrieve_user_group(
            user.id, non_existing_group_id
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_other_users_groups(
        self, create_user, authenticate, retrieve_user_group
    ) -> None:
        user = create_user(pk=1)
        authenticate(user)
        other_user_id, non_existing_group_id = 2, 2
        response: Response = retrieve_user_group(
            other_user_id, non_existing_group_id
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
