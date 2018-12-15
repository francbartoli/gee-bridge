import geojson
from geojson.factory import (
    FeatureCollection, Feature, GeometryCollection,
    Point, LineString, Polygon, MultiLineString, MultiPoint, MultiPolygon
)
from shapely.geometry import (
    shape,
    MultiPolygon as multi_polygon,
    Polygon as polygon
)
import geopandas as gpd
import json


def getBestFootprint(footprints):
    """Create an intersection geometry of the footprints of datasets

    Parameters
    ----------
    footprints: list
        Array of footprint as GeoJSON of Polygon or MultiPolygon type

    Raises
    ------
    ValueError
        Error if each item of the array is not a Polygon or MultiPolygon
        geometry

    Returns
    -------
    dict
        GeoJSON of the resulting FeatureCollection
    """

    # TODO: check if footprints is a list
    shapes = []
    # TODO: move block to get geoseries to a private method
    for footprint in footprints:
        if isinstance(
            shape(footprint), multi_polygon
        ) or isinstance(
                shape(footprint), polygon
        ):
            shapes.append(list(shape(footprint)))
        else:
            raise ValueError("Footprints are not Polygon or MultiPolygon")

    geoseries = [gpd.GeoSeries(shape) for shape in shapes]
    geodataframes = [
        gpd.GeoDataFrame({'geometry': geoserie}) for geoserie in geoseries
    ]
    return geodataframes[0].intersection(
        geodataframes[1]
    ).geometry.__geo_interface__


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

    def overlap(self, ft_coll):
        """Check if the GeoJSON overlaps with an external input

        Parameters
        ----------
        ft_coll : dict
            GeoJSON object for the comparison

        Raises
        ------
        ValueError
            Error raised if the geometries are not of type Polygon
            or MultiPolygon

        Returns
        -------
        bool
            True/False if there is at least an overlap
        """

        gdf_ds = gpd.GeoDataFrame.from_features(ft_coll['features'])
        shapes = []
        for geometry in self.geometries:
            if isinstance(shape(geometry), multi_polygon):
                shapes.append(list(shape(geometry)))
            elif isinstance(shape(geometry), polygon):
                shapes.append(shape(geometry))
            else:
                raise ValueError("Geometries are not Polygon or MultiPolygon")
        gs_aoi = [gpd.GeoSeries(shape) for shape in shapes]
        gdf_aoi = [
            gpd.GeoDataFrame({
                'geometry': gs
            }) for gs in gs_aoi
        ]
        gs_res = gdf_aoi[0].intersects(gdf_ds)
        bools = [item[1] for item in gs_res.items()]
        if True in bools:
            return True
        else:
            return False
