import pytest
from pytest_factoryboy import register
from tests.api.factories import ProcessFactory, UserFactory
from rest_framework.test import APIClient


register(UserFactory, "test_user")
register(ProcessFactory)


@pytest.fixture
def user(test_user):
    test_user.username = "test"
    return test_user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_api_client(user, api_client):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def create_process(user):
    return ProcessFactory(name="test_process", owner=user)
