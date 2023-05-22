import pytest
from model_bakery import baker

from users.models import User, UserGroup


@pytest.fixture
def test_user():
    user = baker.make(User, username="test_user")
    yield user
    del user


@pytest.fixture
def test_user_group():
    usergroup = baker.make(UserGroup, name="test_group")
    yield usergroup
    del usergroup


@pytest.mark.django_db
class TestUserModel:
    def test_str_method(self, test_user):
        assert str(test_user) == "test_user"

    def test_delete_method(self, test_user):
        test_user.delete()
        assert test_user.is_active == False


@pytest.mark.django_db
class TestUserGroupModel:
    def test_str_method(self, test_user_group):
        assert str(test_user_group) == "test_group"

    def test_delete_method(self, test_user_group):
        test_user_group.delete()
        assert test_user_group.is_active == False
