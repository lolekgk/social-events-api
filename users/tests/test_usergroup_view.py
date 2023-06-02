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


@pytest.fixture
def group_admin():
    admin = baker.make(User, pk=1)
    yield admin
    del admin


@pytest.fixture
def group_member():
    member = baker.make(User, pk=2)
    yield member
    del member


@pytest.fixture
def usergroup(group_admin, group_member):
    members_set = baker.prepare(User, _quantity=5)
    members_set.append(group_admin)
    members_set.append(group_member)
    group = baker.make(
        UserGroup,
        administrators=[group_admin],
        members=members_set,
    )
    yield group
    del group


@pytest.mark.django_db
class TestCreateUserGroup:
    def test_create_usergroup_as_anonymous_user(
        self, api_client: APIClient, usergroup_payload
    ) -> None:
        response = api_client.post(
            path="/users/1/groups/", data=usergroup_payload, format="json"
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_usergroup_from_other_users_profile_endpoint(
        self, api_client: APIClient, usergroup_payload
    ) -> None:
        user = baker.make(User, pk=2)
        api_client.force_authenticate(user)

        response = api_client.post(
            path="/users/1/groups/", data=usergroup_payload
        )  # go to the groups of user with id 1 instead of currents user - 2

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_usergroup_with_invalid_data_no_name(
        self, api_client: APIClient
    ) -> None:
        user = baker.make(User)
        api_client.force_authenticate(user)
        invalid_payload = {
            "name": "",
            "description": "test_description",
            "members": [],
            "administrators": [],
        }

        response = api_client.post(
            path=f"/users/{user.pk}/groups/",
            data=invalid_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_usergroup_with_invalid_data_not_existing_members(
        self, api_client: APIClient
    ) -> None:
        user = baker.make(User)
        api_client.force_authenticate(user)
        invalid_payload = {
            "name": "",
            "description": "test_description",
            "members": [2, 3, 4, 5],
            "administrators": [],
        }

        response = api_client.post(
            path=f"/users/{user.pk}/groups/",
            data=invalid_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_usergroup_with_invalid_data_not_existing_administrators(
        self, api_client: APIClient
    ) -> None:
        user = baker.make(User)
        api_client.force_authenticate(user)

        invalid_payload = {
            "name": "",
            "description": "test_description",
            "members": [],
            "administrators": [2, 3, 4, 5],
        }
        response = api_client.post(
            path=f"/users/{user.pk}/groups/",
            data=invalid_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_usergroup_with_invalid_data_not_active_user_as_member(
        self, api_client: APIClient
    ) -> None:
        user = baker.make(User)
        api_client.force_authenticate(user)
        not_active_user = baker.make(User, is_active=False)
        invalid_payload = {
            "name": "test_name",
            "description": "test_description",
            "members": [not_active_user.pk],
            "administrators": [],
        }

        response = api_client.post(
            path=f"/users/{user.pk}/groups/",
            data=invalid_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        usergroup = UserGroup.objects.get(id=response.data["id"])

        assert usergroup is not None
        assert user in usergroup.administrators.all()
        assert user in usergroup.members.all()
        assert not_active_user not in usergroup.members.all()

    def test_create_usergroup_with_invalid_data_not_active_user_as_administrator(
        self, api_client: APIClient
    ) -> None:
        user = baker.make(User)
        api_client.force_authenticate(user)
        not_active_user = baker.make(User, is_active=False)
        invalid_payload = {
            "name": "test_name",
            "description": "test_description",
            "members": [],
            "administrators": [not_active_user.pk],
        }

        response = api_client.post(
            path=f"/users/{user.pk}/groups/",
            data=invalid_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        usergroup = UserGroup.objects.get(id=response.data["id"])

        assert usergroup is not None
        assert user in usergroup.administrators.all()
        assert user in usergroup.members.all()
        assert not_active_user not in usergroup.administrators.all()

    def test_create_usergroup_with_valid_data(
        self, api_client: APIClient, usergroup_payload
    ) -> None:
        user = baker.make(User)

        api_client.force_authenticate(user)
        usergroup_payload["members"] = [1, 2]
        usergroup_payload["administrators"] = [1, 2]

        response = api_client.post(
            path=f"/users/{user.pk}/groups/",
            data=usergroup_payload,
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED

        usergroup = UserGroup.objects.get(id=response.data["id"])

        assert usergroup is not None
        assert user in usergroup.administrators.all()
        assert user in usergroup.members.all()

    def test_create_usergroup_with_valid_data_multiple_members(
        self, api_client: APIClient, usergroup_payload
    ) -> None:
        user = baker.make(User)
        api_client.force_authenticate(user)
        members_ids = [member.pk for member in baker.make(User, _quantity=5)]
        usergroup_payload["members"] = members_ids

        response = api_client.post(
            path=f"/users/{user.pk}/groups/",
            data=usergroup_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        usergroup = UserGroup.objects.get(id=response.data["id"])

        assert usergroup is not None
        assert user in usergroup.administrators.all()
        assert user in usergroup.members.all()
        assert usergroup.members.count() == 6

    def test_create_usergroup_with_valid_data_multiple_administrators(
        self, api_client: APIClient, usergroup_payload
    ) -> None:
        user = baker.make(User)
        api_client.force_authenticate(user)
        members_ids = [member.pk for member in baker.make(User, _quantity=5)]
        usergroup_payload["administrators"] = members_ids

        response = api_client.post(
            path=f"/users/{user.pk}/groups/",
            data=usergroup_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        usergroup = UserGroup.objects.get(id=response.data["id"])

        assert usergroup is not None
        assert user in usergroup.administrators.all()
        assert user in usergroup.members.all()
        assert usergroup.administrators.count() == 6


@pytest.mark.django_db
class TestRetrieveUserGroup:
    def test_get_current_user_existing_usergroup(
        self, api_client: APIClient
    ) -> None:
        group_admin = baker.make(User)
        api_client.force_authenticate(group_admin)
        members_set = baker.prepare(User, _quantity=5)
        members_set.append(group_admin)

        group = baker.make(
            UserGroup,
            administrators=[group_admin],
            members=members_set,
        )

        response = api_client.get(
            f"/users/{group_admin.pk}/groups/{group.pk}/", format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == group.name
        assert response.data["description"] == group.description
        assert group_admin.pk in response.data["administrators"]
        assert group_admin.pk in response.data["members"]
        assert len(response.data["members"]) == 6

    def test_get_current_user_non_existing_usergroup(
        self, api_client: APIClient
    ) -> None:
        group_admin = baker.make(User)
        api_client.force_authenticate(group_admin)

        response = api_client.get(
            f"/users/{group_admin.pk}/groups/1/", format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_other_users_usergroup(self, api_client: APIClient) -> None:
        group_admin = baker.make(User)
        api_client.force_authenticate(group_admin)

        response = api_client.get("/users/2/groups/2/", format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_deleted_usergroup(self, api_client: APIClient) -> None:
        group_admin = baker.make(User)
        api_client.force_authenticate(group_admin)
        members_set = baker.prepare(User, _quantity=5)
        members_set.append(group_admin)

        group = baker.make(
            UserGroup,
            administrators=[group_admin],
            members=members_set,
            is_deleted=True,
        )

        response = api_client.get(
            f"/users/{group_admin.pk}/groups/{group.pk}/", format="json"
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestListUserGroup:
    def test_get_current_usergroups(self, api_client: APIClient) -> None:
        group_admin = baker.make(User)
        api_client.force_authenticate(group_admin)
        members_set = baker.prepare(User, _quantity=5)
        members_set.append(group_admin)

        baker.make(
            UserGroup,
            administrators=[group_admin],
            members=members_set,
            _quantity=10,
            is_deleted=False,
        )

        response = api_client.get(
            f"/users/{group_admin.pk}/groups/", format="json"
        )

        assert response.status_code == status.HTTP_200_OK

        groups = response.data["results"]
        # check first and last group members count
        assert response.data["count"] == 10
        assert len(groups[0]["members"]) == 6
        assert len(groups[-1]["members"]) == 6
        assert group_admin.pk in groups[0]["members"]
        assert group_admin.pk in groups[0]["administrators"]

    def test_get_current_usergroups_with_deleted_groups(
        self, api_client: APIClient
    ) -> None:
        group_admin = baker.make(User)
        api_client.force_authenticate(group_admin)
        members_set = baker.prepare(User, _quantity=5)
        members_set.append(group_admin)

        baker.make(
            UserGroup,
            administrators=[group_admin],
            members=members_set,
            _quantity=5,
            is_deleted=False,
        )
        baker.make(
            UserGroup,
            administrators=[group_admin],
            members=members_set,
            _quantity=5,
            is_deleted=True,
        )

        response = api_client.get(
            f"/users/{group_admin.pk}/groups/", format="json"
        )

        assert response.status_code == status.HTTP_200_OK

        groups = response.data["results"]
        # check first and last group members count
        assert response.data["count"] == 5
        assert len(groups[0]["members"]) == 6
        assert len(groups[-1]["members"]) == 6
        assert group_admin.pk in groups[0]["members"]
        assert group_admin.pk in groups[0]["administrators"]

    def test_get_currrent_usergroups_user_without_groups(
        self, api_client: APIClient
    ) -> None:
        group_admin = baker.make(User)
        api_client.force_authenticate(group_admin)

        response = api_client.get(
            f"/users/{group_admin.pk}/groups/", format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_get_other_users_usergroups(self, api_client: APIClient) -> None:
        group_admin = baker.make(User)
        api_client.force_authenticate(group_admin)

        response = api_client.get("/users/2/groups/", format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestUpdateUserGroup:
    def test_update_usergroup_as_admin(
        self, api_client: APIClient, group_admin, usergroup
    ) -> None:
        api_client.force_authenticate(group_admin)

        updated_payload = {
            "name": "updated_test",
            "description": "updated_test",
            "members": [group_admin.pk],
            "administrators": [group_admin.pk],
        }
        response = api_client.put(
            f"/users/{group_admin.pk}/groups/{usergroup.pk}/",
            data=updated_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        updated_usergroup = UserGroup.objects.get(id=response.data["id"])

        assert updated_usergroup.administrators.count() == 1
        assert group_admin in updated_usergroup.administrators.all()
        assert usergroup.members.count() == 1
        assert group_admin in updated_usergroup.members.all()
        assert updated_usergroup.name == "updated_test"
        assert updated_usergroup.description == "updated_test"

    def test_update_other_users_usergroup(
        self, api_client: APIClient, group_admin, usergroup
    ) -> None:
        other_user = baker.make(User)  # other user
        api_client.force_authenticate(group_admin)

        updated_payload = {
            "name": "updated_test",
            "description": "updated_test",
            "members": [group_admin.pk],
            "administrators": [group_admin.pk],
        }
        response = api_client.put(
            f"/users/{other_user.pk}/groups/{usergroup.pk}/",
            data=updated_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_non_existing_user_usergroup(
        self, api_client: APIClient, group_admin, usergroup
    ) -> None:
        api_client.force_authenticate(group_admin)

        updated_payload = {
            "name": "updated_test",
            "description": "updated_test",
            "members": [group_admin.pk],
            "administrators": [group_admin.pk],
        }
        response = api_client.put(
            f"/users/2/groups/{usergroup.pk}/",  # user with id = 2 does not exist
            data=updated_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_usergroup_as_member(
        self, api_client: APIClient, group_member, usergroup
    ) -> None:
        api_client.force_authenticate(group_member)

        updated_payload = {
            "name": "updated_test",
            "description": "updated_test",
            "members": [group_member.pk],
            "administrators": [group_member.pk],
        }
        response = api_client.put(
            f"/users/{group_member.pk}/groups/{usergroup.pk}/",
            data=updated_payload,
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestDeleteUserGroup:
    def test_delete_usergroup_as_admin(
        self, api_client: APIClient, group_admin, usergroup
    ) -> None:
        api_client.force_authenticate(group_admin)
        response = api_client.delete(
            f"/users/{group_admin.pk}/groups/{usergroup.pk}/",
            format="json",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_usergroup_as_member(
        self, api_client: APIClient, group_member, usergroup
    ) -> None:
        api_client.force_authenticate(group_member)
        response = api_client.delete(
            f"/users/{group_member.pk}/groups/{usergroup.pk}/",
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_usergroup_non_existing_usergroup(
        self, api_client: APIClient, group_admin
    ) -> None:
        api_client.force_authenticate(group_admin)
        response = api_client.delete(
            f"/users/{group_admin.pk}/groups/99/",
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
