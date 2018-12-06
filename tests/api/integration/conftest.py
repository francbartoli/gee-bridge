import pytest
from pytest_factoryboy import register
from tests.api.factories import (
    ProcessFactory,
    UserFactory,
    TokenFactory,
    seq_aoi,
    seq_toi,
    seq_type,
    seq_inputdata,
    seq_outputdata
)
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.reverse import reverse


register(UserFactory, "test_user")
register(TokenFactory)
register(ProcessFactory)


@pytest.fixture
def user(test_user):
    test_user.username = "test"
    # save method has to be called otherwise the value is not persisted
    test_user.save()
    return test_user


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_api_client(user, api_client):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def jwt_api_client(user, api_client):
    url = reverse("rest_login")
    data = {
        "username": user.username,
        "email": user.email,
        "password": "password"
    }
    resp = api_client.post(url, data=data, format="json")
    jwt = resp.json()["token"]
    # same as headers = {'Authorization': 'JWT {}'.format(jwt)}
    api_client.credentials(HTTP_AUTHORIZATION='JWT {}'.format(jwt))
    return api_client


@pytest.fixture
def create_process(user):
    return ProcessFactory(name="test_process", owner=user)


@pytest.fixture
def create_notowned_process():
    username = "kotest"
    UserFactory(username=username)
    user = User.objects.filter(username=username).first()
    return ProcessFactory(name="test_process", owner=user)


@pytest.fixture
def aoi_outfootprint():
    return seq_aoi(outfootprint=True).poly


@pytest.fixture
def payload_aoi_outfootprint(aoi_outfootprint):
    return {
        "name": "outfootprint test",
        "type": seq_type(),
        "aoi": aoi_outfootprint,
        "toi": seq_toi(),
        "input_data": seq_inputdata("L1"),
        "output_data": seq_outputdata()
    }
