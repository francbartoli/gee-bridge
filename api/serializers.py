from rest_framework import serializers
from .models import Rasterbucket, RasterbucketService, GEEMapService
from django.contrib.auth.models import User


class GEEMapServiceSerializer(serializers.ModelSerializer):
    """Define the GEE map service api representation."""

    owner = serializers.ReadOnlyField(source='owner.username')
    rasterbucketservice = serializers.ReadOnlyField(
        source='rasterbucketservice.name')

    class Meta:
        """Meta class."""

        model = GEEMapService
        fields = (
            'id', 'mapid', 'token', 'url',
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

    class Meta:
        """Meta class."""

        model = RasterbucketService
        fields = (
            'id', 'name', 'done',
            'date_created', 'date_modified', 'rasterbucket', 'owner')
        read_only_fields = (
            'date_modified',
            'date_created')


class RasterbucketSerializer(serializers.ModelSerializer):
    """Define an actionable rasterbucket api representation
    with child services."""

    owner = serializers.ReadOnlyField(source='owner.username')
    services = RasterbucketServiceSerializer(many=True, read_only=True)
    # created_by = serializers.ReadOnlyField(source='created_by.username')
    # This can be used as processed_by where the task id (
    # part of a big job id) can be referenced

    class Meta:
        """Meta class."""

        model = Rasterbucket
        fields = (
            'id', 'name', 'raster_data', 'owner', 'services',
            'date_created', 'date_modified')
        read_only_fields = (
            'date_created',
            'date_modified')


class UserSerializer(serializers.ModelSerializer):
    """A user serializer to aid in authentication and authorization."""

    rasterbuckets = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Rasterbucket.objects.all())

    class Meta:
        """Map this serializer to the default django user model."""
        model = User
        fields = ('id', 'username', 'rasterbuckets')

    def create(self, validated_data):
        """Create and returns a new user."""
        user = User.objects.create_user(**validated_data)
        return user
