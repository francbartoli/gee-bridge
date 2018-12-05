import pytest
from rest_framework.reverse import reverse
from rest_framework import status


class TestProcessList:

    @pytest.mark.django_db
    def test_user_can_get_process_list(self, user_api_client, create_process):
        url = reverse('process-list')
        response = user_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]['name'] == create_process.name

    @pytest.mark.django_db
    def test_user_cannot_get_notowned_process_list(
        self, jwt_api_client, create_notowned_process
    ):
        url = reverse('process-list')
        response = jwt_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0
