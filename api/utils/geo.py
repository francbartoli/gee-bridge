import geojson
import json


class GeoJsonUtil:
    """Exploit geospatial utilities

    Parameters
    ----------
        geojson: dict

    """

    def __init__(self, geojson):
        self.geojson = geojson

    @property
    def instance(self):
        """Create geojson instance from a defined json key"""
        try:
            if isinstance(self.geojson, dict):
                gj_instance = geojson.loads(json.dumps(self.geojson))
                return gj_instance
        except KeyError as e:
            raise Exception(e)

    def validate(self):
        """Validate a geojson object"""
        if not self.instance.is_valid:
            return False
        return True
