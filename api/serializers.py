from rest_framework import serializers
from .models import Rasterbucket  # , RasterbucketItem
from django.contrib.auth.models import User


class RasterbucketSerializer(serializers.ModelSerializer):
    """Define an actionable rasterbucket api representation
    with child items."""

    owner = serializers.ReadOnlyField(source='owner.username')

    # items = RasterbucketItemSerializer(many=True, read_only=True)
    # created_by = serializers.ReadOnlyField(source='created_by.username')
    # This can be used as processed_by where the task id (
    # part of a big job id) can be referenced

    class Meta:
        """Meta class."""

        model = Rasterbucket
        fields = (
            'id', 'name', 'raster_data', 'owner',  # 'items',
            'date_created', 'date_modified',)  # 'created_by')
        read_only_fields = ('date_created', 'date_modified')


class UserSerializer(serializers.ModelSerializer):
    """A user serializer to aid in authentication and authorization."""

    rasterbucket = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Rasterbucket.objects.all())

    class Meta:
        """Map this serializer to the default django user model."""
        model = User
        fields = ('id', 'username', 'rasterbucket')
