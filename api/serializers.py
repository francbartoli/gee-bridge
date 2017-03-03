from rest_framework import serializers
from .models import Rasterbucket#, RasterbucketItem


class RasterbucketSerializer(serializers.ModelSerializer):
    """Define an actionable rasterbucket api representation
    with child items."""

    # items = RasterbucketItemSerializer(many=True, read_only=True)
    # created_by = serializers.ReadOnlyField(source='created_by.username')
    # This can be used as processed_by where the task id (
    # part of a big job id) can be referenced

    class Meta:
        """Meta class."""

        model = Rasterbucket
        fields = (
            'id', 'name', 'raster_data',  # 'items',
            'date_created', 'date_modified',)  # 'created_by')
        read_only_fields = ('date_created', 'date_modified')
