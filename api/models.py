"""Summary

Attributes:
    DEFAULT_OWNER (int): Description
    gd_storage (TYPE): Description
    GOOGLE_DRIVE_UPLOAD_FOLDER (str): Description
"""
# TODO implement choices as Enum class
# https://hackernoon.com/using-enum-as-model-field-choice-in-django-92d8b97aaa63
from __future__ import unicode_literals

import re
import uuid
# import json
from collections import OrderedDict, namedtuple

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from gee_bridge import settings
# from jsonfield_compat.fields import JSONField
from jsonfield import JSONField
from polymorphic.models import PolymorphicModel
from rest_framework.authtoken.models import Token

# Create your models here.
DEFAULT_OWNER = 1


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
    name = models.CharField(max_length=255, blank=False, unique=True)
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
    """This class represents the process model

    Attributes:
        id (TYPE): Description
        input_data (TYPE): Description
        output_data (TYPE): Description
        owner (TYPE): Description
    """
    id = models.UUIDField(
        primary_key=True,
        help_text="Process identifier",
        default=uuid.uuid4
    )
    owner = models.ForeignKey(
        'auth.User',
        default=DEFAULT_OWNER,
        related_name='processes',
        on_delete=models.CASCADE)
    input_data = JSONField(
        null=True,
        blank=True,
        default={},
        load_kwargs={'object_pairs_hook': OrderedDict}
    )
    output_data = JSONField(
        null=True,
        blank=True,
        default={},
        load_kwargs={'object_pairs_hook': OrderedDict}
    )

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
    """Summary

    Args:
        sender (TYPE): Description
        instance (TYPE): Description
        created (TYPE): Description
        **kwargs: Description

    Raises:
        Exception: Description
    """
    from api.process.wapor import Wapor
    input_data = instance.input_data
    # TODO must be added also in a serializer for validation id:1 gh:7
    if "process" not in input_data:
        raise Exception("process must be specified")
    args = list()
    proc = input_data.get("process")
    args.insert(1, proc)
    input_data.pop("process", None)
    arguments = input_data.get("arguments")
    optionals = dict()
    for argument in arguments:
        print argument
        if argument.get("positional"):
            argument.pop("positional")
            poslst = argument.values()
            if isinstance(poslst, list):
                for k in (v for elem in poslst for v in elem):
                    b = k.values()
                    for el in b:
                        print args
                        args.append(el)
        else:
            argument.pop("positional")
            if argument.get("choice"):
                argument.pop("choice")
                options = ('c', 'g', 'w')
                try:
                    argkey = argument.keys()[0]
                    data = argument.get(argkey)
                    option = data.get("option")
                    if (isinstance(data, dict) and (option in options)):
                        # julail the cuccudrail
                        # Jemon the king
                        # Plutonio the star
                        Argument = namedtuple('Argument',
                                              ['option', 'choices']
                                              )
                        inner_arg = Argument(data.get("option"),
                                             data.get("choices")
                                             )
                        tpl = tuple(inner_arg)
                        argument[argkey] = list(tpl)
                        optionals.update(argument)
                    else:
                        raise Exception("Option must be in " + options)
                except Exception as e:
                    print e
                    pass
            else:
                optionals.update(argument)
    print 'args=', args
    print 'optionals=', optionals
    process = Wapor()
    cmd_result = process.run(*args, **optionals)
    # TODO async id:6 gh:12
    output_data = cmd_result
    # from IPython import embed
    # embed()
    if created:
        Process.objects.filter(
            id=instance.id
        ).update(
            output_data=output_data
        )


post_save.connect(run_process, sender=Process)
