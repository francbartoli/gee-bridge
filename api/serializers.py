from rest_framework import serializers
from django.contrib.auth.models import User
from api import models


class MapServiceSerializer(serializers.ModelSerializer):
    """Define the map service api representation."""

    owner = serializers.ReadOnlyField(source='owner.username')
    rasterbucketservice = serializers.ReadOnlyField(
        source='rasterbucketservice.name')

    class Meta:
        """Meta class."""

        model = models.BaseServiceModel
        fields = (
            'id', 'url',
            'date_created', 'date_modified',
            'rasterbucketservice', 'owner')
        read_only_fields = (
            'url',
            'date_modified',
            'date_created')

    def to_representation(self, obj):
        """
        Because BaseServiceModel is Polymorphic
        """
        if isinstance(obj, models.GEEMapService):
            return GEEMapServiceSerializer(obj, context=self.context).to_representation(obj)
        elif isinstance(obj, models.TileMapService):
           return TileMapServiceSerializer(obj, context=self.context).to_representation(obj)
        return super(MapServiceSerializer, self).to_representation(obj)


class GEEMapServiceSerializer(serializers.ModelSerializer):
    """Define the GEE map service api representation."""

    owner = serializers.ReadOnlyField(source='owner.username')
    rasterbucketservice = serializers.ReadOnlyField(
        source='rasterbucketservice.name')

    class Meta:
        """Meta class."""

        model = models.GEEMapService
        fields = (
            'id', 'mapid', 'token', 'hashid', 'url',
            'date_created', 'date_modified',
            'rasterbucketservice', 'owner')
        read_only_fields = (
            'url',
            'hashid',
            'date_modified',
            'date_created')


class TileMapServiceSerializer(serializers.ModelSerializer):
    """Define the tile map service api representation."""

    owner = serializers.ReadOnlyField(source='owner.username')
    rasterbucketservice = serializers.ReadOnlyField(
        source='rasterbucketservice.name')

    class Meta:
        """Meta class."""

        model = models.TileMapService
        fields = (
            'id', 'friendly_name', 'geemap', 'url',
            'date_created', 'date_modified',
            'rasterbucketservice', 'owner')
        read_only_fields = (
            'url',
            'date_modified',
            'date_created')


class RasterbucketServiceSerializer(serializers.ModelSerializer):
    """Define the rasterbucket service api representation."""

    owner = serializers.ReadOnlyField(source='owner.username')
    rasterbucket = serializers.ReadOnlyField(source='rasterbucket.name')
    maps = MapServiceSerializer(many=True, read_only=True)

    class Meta:
        """Meta class."""

        model = models.RasterbucketService
        fields = (
            'id', 'name', 'done', 'maps',
            'date_created', 'date_modified', 'rasterbucket', 'owner')
        read_only_fields = (
            'date_modified',
            'date_created')


class RasterbucketSerializer(serializers.ModelSerializer):
    """Define an actionable rasterbucket api representation
    with child services."""

    owner = serializers.ReadOnlyField(source='owner.username')
    services = RasterbucketServiceSerializer(many=True, read_only=True)
    # services = serializers.PrimaryKeyRelatedField(
    #     many=True, queryset=models.RasterbucketService.objects.all())
    # created_by = serializers.ReadOnlyField(source='created_by.username')
    # This can be used as processed_by where the task id (
    # part of a big job id) can be referenced

    class Meta:
        """Meta class."""

        model = models.Rasterbucket
        fields = (
            'id', 'name', 'raster_data', 'owner', 'services',
            'date_created', 'date_modified')
        read_only_fields = (
            'date_created',
            'date_modified')


class UserSerializer(serializers.ModelSerializer):
    """A user serializer to aid in authentication and authorization."""

    rasterbuckets = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Rasterbucket.objects.all())

    class Meta:
        """Map this serializer to the default django user model."""
        model = User
        fields = ('id', 'username', 'rasterbuckets')

    def create(self, validated_data):
        """Create and returns a new user."""
        user = User.objects.create_user(**validated_data)
        return user
