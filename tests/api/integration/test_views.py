import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from tests.api.factories import ProcessFactory
from rest_framework import status
from rest_framework.test import APITestCase


class TestProcessList(APITestCase):

    def setUp(self):
        """Define the test client and other test variables.
        """
        user = User.objects.create(username="test")

        self.expected = 3
        for _ in range(self.expected):
            ProcessFactory()

        # Initialize client and force it to use authentication
        self.client.force_authenticate(user=user)

    @pytest.mark.django_db
    def test_can_get_process_list(self):
        url = reverse('process-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)
