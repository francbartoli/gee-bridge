from __future__ import unicode_literals

from django.db import models
from gdstorage.storage import GoogleDriveStorage
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.dispatch import receiver

# Define Google Drive Storage
gd_storage = GoogleDriveStorage()
# Create your models here.
DEFAULT_OWNER = 1
GOOGLE_DRIVE_UPLOAD_FOLDER = 'myfolder'


class Rasterbucket(models.Model):
    """This class represents the rasterbucket model."""
    name = models.CharField(max_length=255, blank=False, unique=True)
    raster_data = models.FileField(
        upload_to=GOOGLE_DRIVE_UPLOAD_FOLDER,
        # default='myraster',
        blank=True,
        storage=gd_storage)
    owner = models.ForeignKey(
        'auth.User',
        default=DEFAULT_OWNER,
        related_name='rasterbuckets',
        on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Return a human readable representation of the model instance."""
        return "{}".format(self.name)


# This receiver handles token creation when a new user is created.
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
