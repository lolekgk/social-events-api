import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User, UserGroup


@pytest.fixture
def usergroup_payload():
    payload = {
        "name": "test",
        "description": "test",
        "members": [],
        "administrators": [],
    }
    yield payload
    del payload


@pytest.mark.django_db
class TestCreateUserGroup:
    def test_create_user_group_as_anonymous_user(
        self, api_client: APIClient, usergroup_payload
    ) -> None:
        response = api_client.post(
            path="/users/1/groups/", data=usergroup_payload, format="json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_user_group_from_other_users_profile_endpoint(
        self, api_client: APIClient, usergroup_payload
    ) -> None:
        user = baker.make(User, pk=2)
        api_client.force_authenticate(user)

        response = api_client.post(
            path="/users/1/groups/", data=usergroup_payload
        )  # go to the groups of user with id 1 instead of currents user - 2

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_user_group_with_invalid_data_no_name(
        self, api_client: APIClient
    ) -> None:
        user = baker.make(User, pk=1)
        api_client.force_authenticate(user)
        invalid_payload = {
            "name": "",
            "description": "test_description",
            "members": [],
            "administrators": [],
        }

        response = api_client.post(
            path="/users/1/groups/", data=invalid_payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_group_with_invalid_data_not_existing_members(
        self, api_client: APIClient
    ) -> None:
        user = baker.make(User, pk=1)
        api_client.force_authenticate(user)
        invalid_payload = {
            "name": "",
            "description": "test_description",
            "members": [2, 3, 4, 5],
            "administrators": [],
        }

        response = api_client.post(
            path="/users/1/groups/", data=invalid_payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_group_with_invalid_data_not_existing_administrators(
        self, api_client: APIClient
    ) -> None:
        user = baker.make(User, pk=1)
        api_client.force_authenticate(user)

        invalid_payload = {
            "name": "",
            "description": "test_description",
            "members": [],
            "administrators": [2, 3, 4, 5],
        }
        response = api_client.post(
            path="/users/1/groups/", data=invalid_payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # TODO uncomment it after adding this functionality
    def test_create_user_group_with_invalid_data_not_active_user_as_member(
        self, api_client: APIClient
    ) -> None:
        user = baker.make(User, pk=1)
        not_active_user = baker.make(User, pk=2, is_active=False)
        api_client.force_authenticate(user)
        invalid_payload = {
            "name": "test_name",
            "description": "test_description",
            "members": [not_active_user.pk],
            "administrators": [],
        }

        response = api_client.post(
            path="/users/1/groups/", data=invalid_payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_group_with_invalid_data_not_active_user_as_administrator(
        self, api_client: APIClient
    ) -> None:
        user = baker.make(User, pk=1)
        not_active_user = baker.make(User, pk=2, is_active=False)
        api_client.force_authenticate(user)
        invalid_payload = {
            "name": "test_name",
            "description": "test_description",
            "members": [],
            "administrators": [not_active_user.pk],
        }

        response = api_client.post(
            path="/users/1/groups/", data=invalid_payload, format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_user_group_with_valid_data(
        self, api_client: APIClient, usergroup_payload
    ) -> None:
        user = baker.make(User, pk=1)
        api_client.force_authenticate(user)

        response = api_client.post(
            path="/users/1/groups/", data=usergroup_payload, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED

        user_group = UserGroup.objects.get(id=response.data["id"])

        assert user_group is not None
        assert user in user_group.administrators.all()
        assert user in user_group.members.all()

    def test_create_user_group_with_valid_data_multiple_members(
        self, api_client: APIClient, usergroup_payload
    ) -> None:
        user = baker.make(User, pk=1)
        members_ids = [member.pk for member in baker.make(User, _quantity=5)]
        api_client.force_authenticate(user)
        usergroup_payload["members"] = members_ids

        response = api_client.post(
            path="/users/1/groups/", data=usergroup_payload, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED

        user_group = UserGroup.objects.get(id=response.data["id"])

        assert user_group is not None
        assert user in user_group.administrators.all()
        assert user in user_group.members.all()
        assert user_group.members.count() == 6

    def test_create_user_group_with_valid_data_multiple_administrators(
        self, api_client: APIClient, usergroup_payload
    ) -> None:
        user = baker.make(User, pk=1)
        members_ids = [member.pk for member in baker.make(User, _quantity=5)]
        api_client.force_authenticate(user)
        usergroup_payload["administrators"] = members_ids

        response = api_client.post(
            path="/users/1/groups/", data=usergroup_payload, format="json"
        )

        assert response.status_code == status.HTTP_201_CREATED

        user_group = UserGroup.objects.get(id=response.data["id"])

        assert user_group is not None
        assert user in user_group.administrators.all()
        assert user in user_group.members.all()
        assert user_group.administrators.count() == 6


@pytest.mark.django_db
class TestRetrieveUserGroup:
    def test_get_existing_user_group(self, api_client: APIClient) -> None:
        group_admin = baker.make(User, pk=1)
        member_one = baker.make(User, pk=2)
        member_two = baker.make(User, pk=3)
        api_client.force_authenticate(group_admin)
        group = baker.make(
            UserGroup,
            administrators=[group_admin],
            members=[member_one, member_two, group_admin],
        )

        response = api_client.get(
            f"/users/{group_admin.pk}/groups/{group.pk}/", format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == group.name
        assert response.data["description"] == group.description
        assert group_admin.pk in response.data["administrators"]
        assert group_admin.pk in response.data["members"]
        assert member_two.pk in response.data["members"]
        assert member_one.pk in response.data["members"]

    def test_get_non_existing_user_group(self, api_client: APIClient) -> None:
        group_admin = baker.make(User, pk=1)
        api_client.force_authenticate(group_admin)

        response = api_client.get(
            f"/users/{group_admin.pk}/groups/1/", format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_other_users_groups(self, api_client: APIClient) -> None:
        group_admin = baker.make(User, pk=1)
        api_client.force_authenticate(group_admin)

        response = api_client.get("/users/2/groups/2/", format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_deleted_user_group(self, api_client: APIClient) -> None:
        group_admin = baker.make(User, pk=1)
        member_one = baker.make(User, pk=2)
        member_two = baker.make(User, pk=3)
        api_client.force_authenticate(group_admin)
        group = baker.make(
            UserGroup,
            administrators=[group_admin],
            members=[member_one, member_two, group_admin],
            is_deleted=True,
        )

        response = api_client.get(
            f"/users/{group_admin.pk}/groups/{group.pk}/", format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    # TODO fix it
    def test_not_active_user_group(self, api_client: APIClient) -> None:
        group_admin = baker.make(User, pk=1, is_active=False)
        member_one = baker.make(User, pk=2)
        member_two = baker.make(User, pk=3)
        api_client.force_authenticate(group_admin)
        group = baker.make(
            UserGroup,
            administrators=[group_admin],
            members=[member_one, member_two, group_admin],
        )

        response = api_client.get(
            f"/users/{group_admin.pk}/groups/{group.pk}/", format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
