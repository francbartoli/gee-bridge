from __future__ import unicode_literals

from django.db import models
# from jsonfield_compat.fields import JSONField
from jsonfield import JSONField
from polymorphic.models import PolymorphicModel
from gdstorage.storage import GoogleDriveStorage
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from mycustomdjango import settings
import re
import uuid
from jsonpickle import encode, decode
# import json
import collections

# Define Google Drive Storage
gd_storage = GoogleDriveStorage()
# Create your models here.
DEFAULT_OWNER = 1
GOOGLE_DRIVE_UPLOAD_FOLDER = 'myfolder'


def normalize(query_string):
    """Return a tuple of words from a query statement"""
    terms = re.compile(r'"([^"]+)"|(\S+)').findall(query_string)
    normspace = re.compile(r'\s{2,}').sub
    return (normspace(' ', (t[0] or t[1]).strip()) for t in terms)


class BaseModel(models.Model):
    """Abstract model with rasterbucket and their services information"""
    name = models.CharField(max_length=255, blank=False, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    @classmethod
    def search(cls, query_string):
        """Searches the model table for words similar to the query string"""
        query_terms = normalize(query_string)
        for word in query_terms:
            query_object = models.Q(**{"name__icontains": word})
            return cls.objects.filter(query_object).order_by('date_created')


class Process(BaseModel):
    """This class represents the process model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    owner = models.ForeignKey(
        'auth.User',
        default=DEFAULT_OWNER,
        related_name='processes',
        on_delete=models.CASCADE)
    input_data = JSONField(null=True,
                           blank=True,
                           default={},
                           load_kwargs={'object_pairs_hook': collections.OrderedDict}
                           )
    output_data = JSONField(null=True,
                            blank=True,
                            default={},
                            load_kwargs={'object_pairs_hook': collections.OrderedDict}
                            )

    def __str__(self):
        """Return a human readable representation of the model instance."""
        return "{}".format(self.name)


class Rasterbucket(BaseModel):
    """This class represents the rasterbucket model."""
    raster_data = models.FileField(
        upload_to=GOOGLE_DRIVE_UPLOAD_FOLDER,
        storage=gd_storage,
        blank=True)
    owner = models.ForeignKey(
        'auth.User',
        default=DEFAULT_OWNER,
        related_name='rasterbuckets',
        on_delete=models.CASCADE)

    def __str__(self):
        """Return a human readable representation of the model instance."""
        return "{}".format(self.name)


class RasterbucketService(BaseModel):
    """A model of the Rasterbucket service table"""
    done = models.BooleanField(default=False)
    owner = models.ForeignKey(User)
    rasterbucket = models.ForeignKey(
        Rasterbucket,
        on_delete=models.CASCADE,
        related_name='services')

    def __str__(self):
        return 'Rasterbucket Service : {}'.format(self.name)


class BaseServiceModel(PolymorphicModel):
    """An abstract model of the Service table"""
    url = models.CharField(max_length=255, blank=True, unique=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)
    rasterbucketservice = models.ForeignKey(
        RasterbucketService,
        on_delete=models.CASCADE,
        related_name='maps')

    class Meta:
        pass
        # abstract = True


class GEEMapService(BaseServiceModel):
    """A model of the Map service table"""
    mapid = models.CharField(max_length=255, blank=False, unique=True)
    token = models.CharField(max_length=255, blank=False, unique=True)
    hashid = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return 'GEE Map Service : {}'.format(self.url)


class TileMapService(BaseServiceModel):
    """A model of the Tile Map service table"""
    friendly_name = models.CharField(max_length=255, blank=True, unique=False)
    geemap = models.OneToOneField(GEEMapService,
                                  related_name='geemap',
                                  on_delete=models.CASCADE)

    def __str__(self):
        return 'Tile Map Service : {}'.format(self.friendly_name)


# This receiver handles token creation when a new user is created.
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# This receiver handles gee url creation when a new gee map service is created
@receiver(pre_save, sender=GEEMapService)
def create_geemap_url(sender, instance, *args, **kwargs):
    m = instance.mapid
    t = instance.token
    url = settings.GEE_PUBLIC_BASE_URL + m + settings.GEE_MAP_TILES_PATTERN + t
    instance.url = url


@receiver(post_save, sender=GEEMapService)
def create_tilemap(sender, instance, created, **kwargs):
    uid = str(instance.hashid)
    url = settings.BASE_URL + settings.PROXY_LOCATION + instance.owner.username + '/' + instance.rasterbucketservice.name + '/' + instance.rasterbucketservice.name + '/' + uid
    name = instance.rasterbucketservice.rasterbucket.name + instance.rasterbucketservice.name
    if created:
        TileMapService.objects.create(geemap=instance,
                                      owner=instance.owner,
                                      rasterbucketservice=instance.rasterbucketservice,
                                      url=url,
                                      friendly_name=name)


pre_save.connect(create_geemap_url, sender=GEEMapService)
post_save.connect(create_tilemap, sender=GEEMapService)


@receiver(post_save, sender=Process)
def run_process(sender, instance, created, **kwargs):
    from webmapping.process.wapor import Wapor
    wapor = Wapor()
    cmd_result = wapor.run()
    # TODO async
    output_data = cmd_result
    if created:
        Process.objects.filter(id=instance.id
                               ).update(output_data=output_data
                                        )


post_save.connect(run_process, sender=Process)
