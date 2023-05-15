import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    client = APIClient()
    client.post
    yield client
    del client


@pytest.fixture
def create_user():
    def do_create_user(pk: int, is_staff=False):
        user = baker.make(User, pk=pk, is_staff=is_staff)
        return user

    return do_create_user


@pytest.fixture
def authenticate(api_client: APIClient):
    def do_authenticate(user):
        return api_client.force_authenticate(user=user)

    return do_authenticate
