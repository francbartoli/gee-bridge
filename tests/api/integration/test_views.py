import pytest
from django.urls import reverse
from rest_framework import status


class TestProcessList:

    @pytest.mark.django_db
    def test_can_get_process_list(self, user_api_client, create_process):
        url = reverse('process-list')
        response = user_api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]['name'] == create_process.name
