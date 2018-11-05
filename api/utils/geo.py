import geojson
from geojson.factory import (
    FeatureCollection, Feature, GeometryCollection,
    Point, LineString, Polygon, MultiLineString, MultiPoint, MultiPolygon
)
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
        """Create geojson instance from a defined json key

        Returns
        -------
            geojson.GeoJSON
                Instance of the GeoJSON class
        """

        try:
            if isinstance(self.geojson, dict):
                gj = geojson.loads(json.dumps(self.geojson))
                return geojson.GeoJSON(gj)
        except KeyError as e:
            raise Exception(e)

    @property
    def type(self):
        """Identify the type of the instance"""

        geojson_types = {
            'Point': Point,
            'MultiPoint': MultiPoint,
            'LineString': LineString,
            'MultiLineString': MultiLineString,
            'Polygon': Polygon,
            'MultiPolygon': MultiPolygon,
            'GeometryCollection': GeometryCollection,
            'Feature': Feature,
            'FeatureCollection': FeatureCollection,
        }

        try:
            for self.instance["type"] in geojson_types.keys():
                return geojson_types.get(self.instance["type"])
        except KeyError as e:
            raise

    @property
    def geometries(self):
        try:
            if isinstance(self.type, FeatureCollection):
                return [ft["geometry"] for ft in self.instance["features"]]
            elif isinstance(self.type, Feature):
                return [self.instance["geometry"]]
            elif isinstance(self.type, GeometryCollection):
                return self.instance["geometries"]
            else:
                return [self.instance]
        except KeyError as e:
            raise

    def validate(self):
        """Validate a geojson object"""
        if not self.instance.is_valid:
            return False
        return True
