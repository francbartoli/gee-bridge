import geojson
import json


class GeoJsonUtil:
    """Exploit geospatial utilities

    Parameters
    ----------
        geojson: dict
            Geojson object to handle
    """

    def __init__(self, geojson):
        self.geojson = geojson

    @property
    def instance(self):
        """Create geojson instance from a defined json key"""
        try:
            if isinstance(self.geojson, dict):
                gj = geojson.loads(json.dumps(self.geojson))
                return geojson.GeoJSON(gj)
        except KeyError as e:
            raise Exception(e)

    def validate(self):
        """Validate a geojson object"""
        if not self.instance.is_valid:
            return False
        return True
