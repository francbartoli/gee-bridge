"""Serializers
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from api import models
from api.exceptions import GEEValidationError
from api.utils.geo import GeoJsonUtil as geojson_util
from api.utils.geo import getBestFootprint as get_best_footprint
from api.utils.gee import GEEUtil as gee_util
from api.utils.gee import tooManyPixels as too_many_pixels


class MapServiceSerializer(serializers.ModelSerializer):
    """Define the map service api representation.

    Attributes:
        owner (TYPE): Description
        rasterbucketservice (TYPE): Description
    """

    owner = serializers.ReadOnlyField(source='owner.username')
    rasterbucketservice = serializers.ReadOnlyField(
        source='rasterbucketservice.name')

    class Meta:
        """Meta class.

        Attributes:
            fields (TYPE): Description
            model (TYPE): Description
            read_only_fields (TYPE): Description
        """

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

        Args:
            obj (TYPE): Description

        Returns:
            TYPE: Description
        """
        if isinstance(obj, models.GEEMapService):
            return GEEMapServiceSerializer(
                obj, context=self.context
            ).to_representation(obj)
        elif isinstance(obj, models.TileMapService):
            return TileMapServiceSerializer(
                obj, context=self.context
            ).to_representation(obj)
        return super(MapServiceSerializer, self).to_representation(obj)


class GEEMapServiceSerializer(serializers.ModelSerializer):
    """Define the GEE map service api representation.

    Attributes:
        owner (TYPE): Description
        rasterbucketservice (TYPE): Description
    """

    owner = serializers.ReadOnlyField(source='owner.username')
    rasterbucketservice = serializers.ReadOnlyField(
        source='rasterbucketservice.name')

    class Meta:
        """Meta class.

        Attributes:
            fields (TYPE): Description
            model (TYPE): Description
            read_only_fields (TYPE): Description
        """

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
    """Define the tile map service api representation.

    Attributes:
        owner (TYPE): Description
        rasterbucketservice (TYPE): Description
    """

    owner = serializers.ReadOnlyField(source='owner.username')
    rasterbucketservice = serializers.ReadOnlyField(
        source='rasterbucketservice.name')

    class Meta:
        """Meta class.

        Attributes:
            fields (TYPE): Description
            model (TYPE): Description
            read_only_fields (TYPE): Description
        """

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
    """Define the rasterbucket service api representation.

    Attributes:
        maps (TYPE): Description
        owner (TYPE): Description
        rasterbucket (TYPE): Description
    """

    owner = serializers.ReadOnlyField(source='owner.username')
    rasterbucket = serializers.ReadOnlyField(source='rasterbucket.name')
    maps = MapServiceSerializer(many=True, read_only=True)

    class Meta:
        """Meta class.

        Attributes:
            fields (TYPE): Description
            model (TYPE): Description
            read_only_fields (TYPE): Description
        """

        model = models.RasterbucketService
        fields = (
            'id', 'name', 'done', 'maps',
            'date_created', 'date_modified', 'rasterbucket', 'owner')
        read_only_fields = (
            'date_modified',
            'date_created')


class RasterbucketSerializer(serializers.ModelSerializer):
    """Define an actionable rasterbucket api representation
    with child services.

    Attributes:
        owner (TYPE): Description
        services (TYPE): Description
    """

    owner = serializers.ReadOnlyField(source='owner.username')
    services = RasterbucketServiceSerializer(many=True, read_only=True)
    # services = serializers.PrimaryKeyRelatedField(
    #     many=True, queryset=models.RasterbucketService.objects.all())
    # created_by = serializers.ReadOnlyField(source='created_by.username')
    # This can be used as processed_by where the task id (
    # part of a big job id) can be referenced

    class Meta:
        """Meta class.

        Attributes:
            fields (TYPE): Description
            model (TYPE): Description
            read_only_fields (TYPE): Description
        """

        model = models.Rasterbucket
        fields = (
            'id', 'name', 'raster_data', 'owner', 'services',
            'date_created', 'date_modified')
        read_only_fields = (
            'date_created',
            'date_modified')


class ProcessSerializer(serializers.ModelSerializer):
    """Define an actionable process api serializer.

    Parameters
    ----------
        type: dict
            Type of a process
        owner: string
            Owner of a process
        aoi: dict
            Area of interest GeoJson formatted,
            it can be multiple
        toi: dict
            Time of interest, it can be multiple
        input_data: dict
            Input data for a process
        output_data: dict
            Output data for a process
        status: string
            State of the process job
    """

    type = serializers.JSONField()
    owner = serializers.ReadOnlyField(source='owner.username')
    aoi = serializers.JSONField()
    toi = serializers.JSONField()
    input_data = serializers.JSONField()
    output_data = serializers.JSONField()
    status = serializers.ReadOnlyField()

    def validate(self, data):
        """
        Check if several semantic rules are met
        """

        # TODO: avoid the assumption that aoi is an one item array
        aoi = data["aoi"][0]
        inputs = data["input_data"]["inputs"]
        datasets = [
            (
                input["dataset"],
                input["metadata"],
                input["bands"],
            ) for input in inputs
        ]
        # check if one of the dataset has too many pixels
        for ds in datasets:
            for band in ds[2]:
                if too_many_pixels(ds[0], aoi, band):
                    raise GEEValidationError(
                        "aoi",
                        detail="Area of Interest has too many pixels"
                    )
        # check if aoi and datasets' footprint overlap
        footprints = []
        for dataset in datasets:
            if dataset[1]:
                footprints.append(
                    gee_util(
                        dataset[0]
                    ).getFootprint(metadata=dataset[1][0])
                )
            else:
                footprints.append(
                    gee_util(
                        dataset[0]
                    ).getFootprint(metadata=None)
                )

        best_footprint = get_best_footprint(footprints)
        if not geojson_util(aoi).overlap(best_footprint):
            raise GEEValidationError(
                "aoi",
                detail="Area of Interest out of datasets' footprint"
            )
        return data

    def validate_aoi(self, value):
        """
        Check that the aoi contains valid GeoJSON.
        """

        # can be single or an array of multiple valid geojson
        if not isinstance(value, list):
            try:
                if isinstance(
                    value, dict
                ) and geojson_util(
                    value
                ).validate():
                    return value
                else:
                    raise serializers.ValidationError(
                        "GeoJSON is not valid."
                    )
            except Exception as e:
                raise serializers.ValidationError(
                    "GeoJSON is not valid."
                )
        else:
            for gj_item in value:
                try:
                    if not isinstance(
                        gj_item, dict
                    ) or not geojson_util(
                        gj_item
                    ).validate():
                        raise serializers.ValidationError(
                            "GeoJSON is not valid."
                        )
                except Exception as e:
                    raise serializers.ValidationError(
                        "GeoJSON is not valid."
                    )
            return value

    class Meta:
        """Meta class.
        """

        model = models.Process
        fields = (
            'id', 'name', 'type', 'owner', 'aoi', 'toi', 'input_data',
            'output_data', 'status', 'date_created', 'date_modified')
        read_only_fields = (
            'status',
            'date_created',
            'date_modified')


class UserSerializer(serializers.ModelSerializer):
    """A user serializer to aid in authentication and authorization.

    Attributes:
        rasterbuckets (TYPE): Description
    """

    rasterbuckets = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Rasterbucket.objects.all())
    processes = serializers.PrimaryKeyRelatedField(
        many=True, queryset=models.Process.objects.all())

    class Meta:
        """Map this serializer to the default django user model.

        Attributes:
            fields (tuple): Description
            model (TYPE): Description
        """
        model = User
        fields = ('id', 'username', 'rasterbuckets', 'processes')

    def create(self, validated_data):
        """Create and returns a new user.

        Args:
            validated_data (TYPE): Description

        Returns:
            TYPE: Description
        """
        user = User.objects.create_user(**validated_data)
        return user
