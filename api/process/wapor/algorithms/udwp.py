import logging
from api.utils.geo import GeoJsonUtil
from geojson.geometry import Polygon
from rest_framework.serializers import ValidationError


class UDWP:

    def __init__(self, **kwargs):
        print(kwargs)
        # self.logger = logging.getLogger(__name__, subsystem="algorithms")
        self.__name = "UDWP"
        # filters
        self.__filters = {}
        try:
            if kwargs["filters"]:
                for filter_k, filter_v in kwargs["filters"].items():
                    # extract spatial filter if polygon type
                    if filter_k == "spatial_extent":
                        if self.is_polygon(filter_v):
                            self.__filters['{}'.format(filter_k)] = filter_v
                        else:
                            raise ValidationError(
                                "Area of interest is not a Polygon"
                            )
        except KeyError as e:
            raise
        self.__outputs = {"maps": {}, "stats": {}, "tasks": {}}
        # FIXME into marmee so we can initialize self.__errors as {}
        self.errors = {}

    def execute(self):

        return {"outputs": self.__outputs, "errors": self.errors}

    def is_polygon(self, obj):
        """Retrieve if the spatial extent is of polygon type"""

        type = GeoJsonUtil(obj).type
        if type is not Polygon:
            return False
        else:
            return True
