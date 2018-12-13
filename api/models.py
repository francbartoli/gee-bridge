"""Summary

Attributes:
    DEFAULT_OWNER (int): Description
    gd_storage (TYPE): Description
    GOOGLE_DRIVE_UPLOAD_FOLDER (str): Description
"""
# TODO implement choices as Enum class id:12 gh:23
# https://hackernoon.com/using-enum-as-model-field-choice-in-django-92d8b97aaa63
from __future__ import unicode_literals

import re
import uuid
from collections import OrderedDict, namedtuple

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from gee_bridge import settings
from api.tasks import generate_process
from django.contrib.postgres.fields import JSONField as PGJSONField
from jsonfield import JSONField as SLJSONField
from polymorphic.models import PolymorphicModel
from rest_framework.authtoken.models import Token
# Create your models here.

# init
DEFAULT_OWNER = 1

if settings.INTERNAL_USE_NATIVE_JSONFIELD:
    _JSONField = PGJSONField
else:
    _JSONField = SLJSONField


def normalize(query_string):
    """Return a tuple of words from a query statement

    Args:
        query_string (TYPE): Description

    Returns:
        TYPE: Description
    """
    terms = re.compile(r'"([^"]+)"|(\S+)').findall(query_string)
    normspace = re.compile(r'\s{2,}').sub
    return (normspace(' ', (t[0] or t[1]).strip()) for t in terms)


class BaseModel(models.Model):
    """Abstract model with rasterbucket and their services information

    Attributes:
        date_created (TYPE): Description
        date_modified (TYPE): Description
        name (TYPE): Description
    """
    name = models.CharField(max_length=255, blank=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Summary

        Attributes:
            abstract (bool): Description
        """
        abstract = True

    @classmethod
    def search(cls, query_string):
        """Searches the model table for words similar to the query string

        Args:
            query_string (TYPE): Description

        Returns:
            TYPE: Description
        """
        query_terms = normalize(query_string)
        for word in query_terms:
            query_object = models.Q(**{"name__icontains": word})
            return cls.objects.filter(query_object).order_by('date_created')


class Process(BaseModel):
    """Model the process interface

    Parameters
    ----------
        id: str
            An unique identifier for the process
        type: dict
            A type of the process identified by a namespace,
            algorithm and execution mode which can be sync/async
        owner: string
            A user who owns the process
        aoi: dict
            An area of interest or multiple areas
        toi: dict
            A period of interest or multiple periods
        input_data: dict
            Data with input datasets
        output_data: dict
            Data with output maps, stats, tasks, errors
        status: str
            State of the processing job
    """

    STATUS_PENDING = "pending"
    STATUS_FAILED = "failed"
    STATUS_DONE = "done"
    STATUSES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_FAILED, "Failed"),
        (STATUS_DONE, "Done"),
    ]

    class Meta:
        db_table = 'process'
        managed = True
        verbose_name = 'Process'
        verbose_name_plural = 'Processes'

    id = models.UUIDField(
        primary_key=True,
        help_text="Process identifier",
        default=uuid.uuid4
    )
    type = _JSONField(
        null=True,
        blank=True,
        default={}
    )
    owner = models.ForeignKey(
        'auth.User',
        default=DEFAULT_OWNER,
        related_name='processes',
        on_delete=models.CASCADE
    )
    aoi = _JSONField(
        null=True,
        blank=True,
        default=[]
    )
    toi = _JSONField(
        null=True,
        blank=True,
        default=[]
    )
    input_data = _JSONField(
        null=True,
        blank=True,
        default={}  # ,
        # load_kwargs={'object_pairs_hook': OrderedDict}
    )
    output_data = _JSONField(
        null=True,
        blank=True,
        default={}  # ,
        # load_kwargs={'object_pairs_hook': OrderedDict}
    )
    status = models.CharField(
        max_length=10,
        default=STATUS_PENDING,
        choices=STATUSES,
    )
    # TODO validate against a json schema
    # https://stackoverflow.com/questions/37642742/django-postgresql-json-field-schema-validation

    def __str__(self):
        """Return a human readable representation of the model instance.

        Returns:
            TYPE: Description
        """
        return "{}".format(self.name)


class Rasterbucket(BaseModel):
    """This class represents the rasterbucket model.

    Attributes:
        owner (TYPE): Description
        raster_data (TYPE): Description
    """
    raster_data = models.FileField(
        upload_to=settings.GOOGLE_CLOUD_STORAGE_UPLOAD_FOLDER,
        blank=True)
    owner = models.ForeignKey(
        'auth.User',
        default=DEFAULT_OWNER,
        related_name='rasterbuckets',
        on_delete=models.CASCADE)

    def __str__(self):
        """Return a human readable representation of the model instance.

        Returns:
            TYPE: Description
        """
        return "{}".format(self.name)


class RasterbucketService(BaseModel):
    """A model of the Rasterbucket service table

    Attributes:
        done (TYPE): Description
        owner (TYPE): Description
        rasterbucket (TYPE): Description
    """
    done = models.BooleanField(default=False)
    owner = models.ForeignKey(User)
    rasterbucket = models.ForeignKey(
        Rasterbucket,
        on_delete=models.CASCADE,
        related_name='services')

    def __str__(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return 'Rasterbucket Service : {}'.format(self.name)


class BaseServiceModel(PolymorphicModel):
    """An abstract model of the Service table

    Attributes:
        date_created (TYPE): Description
        date_modified (TYPE): Description
        owner (TYPE): Description
        rasterbucketservice (TYPE): Description
        url (TYPE): Description
    """
    url = models.CharField(max_length=255, blank=True, unique=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User)
    rasterbucketservice = models.ForeignKey(
        RasterbucketService,
        on_delete=models.CASCADE,
        related_name='maps')

    class Meta:
        """Summary
        """
        pass
        # abstract = True


class GEEMapService(BaseServiceModel):
    """A model of the Map service table

    Attributes:
        hashid (TYPE): Description
        mapid (TYPE): Description
        token (TYPE): Description
    """
    mapid = models.CharField(max_length=255, blank=False, unique=True)
    token = models.CharField(max_length=255, blank=False, unique=True)
    hashid = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return 'GEE Map Service : {}'.format(self.url)


class TileMapService(BaseServiceModel):
    """A model of the Tile Map service table

    Attributes:
        friendly_name (TYPE): Description
        geemap (TYPE): Description
    """
    friendly_name = models.CharField(max_length=255, blank=True, unique=False)
    geemap = models.OneToOneField(GEEMapService,
                                  related_name='geemap',
                                  on_delete=models.CASCADE)

    def __str__(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return 'Tile Map Service : {}'.format(self.friendly_name)


# This receiver handles token creation when a new user is created.
@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """Summary

    Args:
        sender (TYPE): Description
        instance (None, optional): Description
        created (bool, optional): Description
        **kwargs: Description
    """
    if created:
        Token.objects.create(user=instance)


# This receiver handles gee url creation when a new gee map service is created
@receiver(pre_save, sender=GEEMapService)
def create_geemap_url(sender, instance, *args, **kwargs):
    """Summary

    Args:
        sender (TYPE): Description
        instance (TYPE): Description
        *args: Description
        **kwargs: Description
    """
    m = instance.mapid
    t = instance.token
    url = settings.GEE_PUBLIC_BASE_URL + m + settings.GEE_MAP_TILES_PATTERN + t
    instance.url = url


@receiver(post_save, sender=GEEMapService)
def create_tilemap(sender, instance, created, **kwargs):
    """Summary

    Args:
        sender (TYPE): Description
        instance (TYPE): Description
        created (TYPE): Description
        **kwargs: Description
    """
    uid = str(instance.hashid)
    url = settings.BASE_URL + settings.PROXY_LOCATION + instance.owner.username + '/' + \
        instance.rasterbucketservice.name + '/' + \
        instance.rasterbucketservice.name + '/' + uid
    name = instance.rasterbucketservice.rasterbucket.name + \
        instance.rasterbucketservice.name
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
    """Signal for triggering the run of processes on post-save

    Parameters
    ----------
        sender: Process
            The model that triggers the signal
        instance: Process
            Instance of the Process model
        created: boolean
            Property that indicates if the instance is saved
        kwargs: dict

    Raises:
        Exception: Description
    """
    from api.process.wapor.wapor import Wapor
    type = instance.type
    aois = instance.aoi
    tois = instance.toi
    input_data = instance.input_data

    mode = type.get("mode")
    # TODO search in the catalog for validation of namespace
    algorithm = type["wapor"].get("template")
    # TODO cycle over all multiple aoi
    aoi = aois[0]
    # TODO cycle over all multiple toi
    toi = tois[0]
    inputs = input_data.get("inputs")

    kwargs = dict(
        wapor_name=instance.name,
        wapor_inputs=inputs,
        wapor_options=dict(
            spatial_extent=aoi,
            temporal_extent=toi
        )
    )

    process = Wapor(**kwargs)

    if created:
        if mode == "sync":
            process_result = process.run(algorithm)
            # TODO async id:6 gh:12
            output_data = [process_result]
            Process.objects.filter(
                id=instance.id
            ).update(
                output_data=output_data,
                status=Process.STATUS_DONE
            )
        if mode == "async":
            generate_process.send(instance.id, process, algorithm)


post_save.connect(run_process, sender=Process)
