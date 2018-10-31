import logging
from api.utils.geo import GeoJsonUtil
from geojson.geometry import Polygon
from rest_framework.serializers import ValidationError


class UDWP:

    def __init__(self, **kwargs):

        self.logger = logging.getLogger(__name__)
        self.__name = "UDWP"
        # filters
        self.__filters = {}
        self.logger.debug("Received kwargs are:\n{}".format(kwargs))
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
