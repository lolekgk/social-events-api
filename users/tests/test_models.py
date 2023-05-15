import pytest

from users.models import User, UserGroup


@pytest.fixture
def test_user():
    user = User.objects.create(
        username="test_user",
        password="test_password",
        email="test@email.com",
        first_name="Arnolds",
        last_name="Schwarz",
    )
    yield user
    del user


@pytest.fixture
def test_user_group(test_user):
    usergroup = UserGroup.objects.create(name="test_group")
    usergroup.administrators.add(test_user)
    usergroup.members.add(test_user)
    yield usergroup
    del usergroup


@pytest.mark.django_db
class TestUserModel:
    def test_str_method(self, test_user):
        assert str(test_user) == "test_user"

    def test_custom_delete_method(self, test_user):
        test_user.delete()
        assert test_user.is_active == False


@pytest.mark.django_db
class TestUserGroupModel:
    def test_str_method(self, test_user_group):
        assert str(test_user_group) == "test_group"

    def test_custom_delete_method(self, test_user_group):
        test_user_group.delete()
        assert test_user_group.is_active == False
