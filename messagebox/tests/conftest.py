import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    client = APIClient()
    yield client
    del client


@pytest.fixture
def test_sender():
    sender = baker.make(User, username="test_sender")
    yield sender
    del sender


@pytest.fixture
def test_receiver():
    receiver = baker.make(User, username="test_receiver")
    yield receiver
    del receiver
