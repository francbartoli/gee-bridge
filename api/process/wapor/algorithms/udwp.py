import logging
from api.utils.geo import GeoJsonUtil
from geojson.geometry import Polygon
from collections import namedtuple
from rest_framework.serializers import ValidationError


class UDWP:

    def __init__(self, **kwargs):

        Collection = namedtuple(
            'Collection',
            ['name', 'id', 'metadata', 'bands']
        )

        self.logger = logging.getLogger(__name__)
        self.__name = "UDWP"
        self.logger.debug("Received kwargs are:\n{}".format(kwargs))
        # inputs
        self.npp = Collection(name="NPP", id="", metadata={}, bands=[])
        self.aeti = Collection(name="AETI", id="", metadata={}, bands=[])
        try:
            if kwargs["inputs"]:
                for input in kwargs["inputs"]:
                    if "NPP" in input["dataset"]:
                        self.npp._replace(id=input["dataset"])
                        self.npp._replace(metadata=input["metadata"])
                        self.npp._replace(bands=input["bands"])
                    elif "AETI" in input["dataset"]:
                        self.aeti._replace(id=input["dataset"])
                        self.aeti._replace(metadata=input["metadata"])
                        self.aeti._replace(bands=input["bands"])
                    else:
                        raise ValidationError(
                            "Input datasets are not valid for Water Productivity"
                        )
        except KeyError as e:
            raise
        # filters
        self.__filters = {}
        try:
            if kwargs["filters"]:
                for filter_k, filter_v in kwargs["filters"].items():
                    # extract spatial filter if polygon type and add it
                    if filter_k == "spatial_extent":
                        if self.is_polygon(filter_v):
                            self.__filters['{}'.format(filter_k)] = filter_v
                        else:
                            self.logger.error(
                                "GeoJSON type from aoi is not of type Polygon"
                            )
                            raise ValidationError(
                                "Area of interest is not a Polygon"
                            )
                    # extract temporal filter and add it
                    if filter_k == "temporal_extent":
                        self.__filters['{}'.format(filter_k)] = filter_v
        except KeyError as e:
            self.logger.exception("KeyError exception")
            raise
        self.__outputs = {"maps": {}, "stats": {}, "tasks": {}}
        # FIXME into marmee so we can initialize self.__errors as {}
        self.errors = {}

    def execute(self):

        return {"outputs": self.__outputs, "errors": self.errors}

    def is_polygon(self, obj):
        """Retrieve if the spatial extent is of polygon type"""

        type = GeoJsonUtil(obj).type
        self.logger.debug("GeoJSON type is {}".format(type))
        if type is not Polygon:
            return False
        else:
            return True
