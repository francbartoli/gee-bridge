from django.test import TestCase
from .models import Rasterbucket
from django.contrib.auth.models import User

# Create your tests here.


class ModelTestCase(TestCase):
    """This class defines the test suite for the rasterbucket"""

    def setUp(self):
        """Define the test client and other test variables."""
        user = User.objects.create(username="nerd")
        self.name = "Write world class rasters"
        # specify owner of a rasterbucket
        self.rasterbucket = Rasterbucket(name=self.name, owner=user)

    def test_model_can_create_a_rasterbucket(self):
        """Test the rasterbucket model can create a rasterbucket."""
        old_count = Rasterbucket.objects.count()
        self.rasterbucket.save()
        new_count = Rasterbucket.objects.count()
        self.assertNotEqual(old_count, new_count)
