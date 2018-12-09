from ee import (
    ImageCollection,
    FeatureCollection,
    Image,
    Filter,
    Geometry,
    EEException
)
from ee.data import (
    getInfo,
    ASSET_TYPE_FOLDER,
    ASSET_TYPE_IMAGE_COLL,
    DEFAULT_TILE_BASE_URL
)
from api.utils.redux import (
    createImageMeanDictByRegion,
    createImageSumDictByRegion,
    createImageMinMaxDictByRegion,
    createImageNumPixelsDictByRegion
)
from rest_framework.serializers import ValidationError
from collections import namedtuple


Collection = namedtuple('Collection', ['name', 'id', 'metadata', 'bands'])


def createInstanceUrl(inst):
    """Create an earth engine tile service url for an instance

    Parameters
    ----------
    inst: ee.ImageCollection or ee.Image
        ImageCollection or Image instance

    Returns
    -------
    str
        Url string of the earth engine service

    """

    try:
        r = inst.getMapId()
    except EEException as e:
        raise

    return "{}/map/{}/{{z}}/{{x}}/{{y}}?token={}".format(
        DEFAULT_TILE_BASE_URL,
        r["mapid"],
        r["token"]
    )


def createCollectionStat(coll_inst, band):
    """Create an earth engine statistic for a collection instance

    Parameters
    ----------
    coll_inst : ee.ImageCollection
        ImageCollection instance
    band: str
        Band where to get statistics

    Returns
    -------
    dict
        Dictionary of the statistic for the evaluated collection

    """

    return coll_inst.aggregate_stats(band).getInfo()["values"]


def createImageStat(img_inst, region, band, sum=False):
    """Create an earth engine statistic for an image instance

    Parameters
    ----------
    img_inst: ee.Image
        Image instance
    region: ee.Geometry
        Geometry of the reduced area
    band: str
        Band where to get statistics
    sum: bool
        Boolean value to decide if the sum key is returned

    Returns
    -------
    dict
        Dictionary of the statistic for the evaluated image

    """

    try:
        img_mean = createImageMeanDictByRegion(img_inst, region)
        mean_val = img_mean[band]
        img_min_max = createImageMinMaxDictByRegion(img_inst, region)
        for key in img_min_max.keys():
            if band and "min" in key:
                min_val = img_min_max[key]
            elif band and "max" in key:
                max_val = img_min_max[key]
            else:
                pass
        # TODO: Check the consistency of sum value returned
        img_sum = createImageSumDictByRegion(img_inst, region)
        sum_val = img_sum[band]
        ret = {
            "{}".format(band): {
                "mean": mean_val,
                "min": min_val,
                "max": max_val,
                "sum": sum_val
            }
        }
        if not sum:
            ret[band].pop("sum")
        return ret
    except KeyError:
        ret = {
            "{}".format(band): {
                "mean": None,
                "min": None,
                "max": None,
                "sum": None
            }
        }
        if not sum:
            ret[band].pop("sum")
        return ret


def _getNumPixels(img_inst, region, band):
    return createImageNumPixelsDictByRegion(img_inst, region)[band]


def tooManyPixels(collection, geometry, band):
    """Check if the collection has too many pixels for the geometry

    Parameters
    ----------
    collection: str
        Asset id of the collection
    geometry: dict
        Geometry in GeoJSON format
    band: str
        Band of the image

    Returns
    -------
    bool
        Boolean value if number is lower than max value 10000000
    """

    coll_inst = ImageCollection(collection)
    geom_inst = Geometry(geometry)
    npixels = _getNumPixels(coll_inst.first(), geom_inst, band)
    if npixels < 10000000:
        return False
    else:
        return True


class GEEUtil:
    """Exploit earth engine utilities

    Parameters
    ----------
        collection: string
            Collection asset id
    """

    def __init__(self, collection):
        self.collection = collection
        self.__reduced = None

    @property
    def instance(self):
        """Create EE instance from a defined asset id"""
        try:
            if isinstance(self.collection, str):
                ee_asset = ImageCollection(self.collection)
                return ee_asset
        except EEException as e:
            raise ValidationError("Input dataset is not valid")

    @property
    def type(self):
        """Identify the type of the instance"""

        asset_types = {
            ASSET_TYPE_IMAGE_COLL: ImageCollection,
            'FeatureCollection': FeatureCollection,
            'Image': Image,
            ASSET_TYPE_FOLDER: None
        }

        try:
            for getInfo(self.collection)["type"] in asset_types.keys():
                return asset_types.get(getInfo(self.collection)["type"])
        except KeyError as e:
            raise

    @property
    def reduced(self):
        """EE reduced instance from asset id and filters"""
        return self.__reduced

    # setters
    @reduced.setter
    def reduced(self, value):
        """Sets new value for attribute reduced

        Parameters
        ----------
        value : string
            Assign new reduced to instance

        """
        self.__reduced = value

    def filterDateRange(self, filter=None):
        """Filter by period of time

        Parameters
        ----------
        filter : ee.Filter, optional
            Filter instance of DateRange object
            (the default is None, which doesn't filter)

        Example
        -------
        >>c = GEEUtil('projects/fao-wapor/L1/L1_AETI_D')
        >>range = DateRange("2017-01-01", "2018-01-01")
        >>f = ee.Filter(range)
        >>c.filterDateRange(filter=f)

        """

        try:
            if filter and isinstance(filter, Filter):
                try:
                    if not self.reduced:
                        redux = self.instance.filterDate(filter).sort(
                            'system:time_start', True
                        )
                    else:
                        redux = self.reduced.filterDate(filter).sort(
                            'system:time_start', True
                        )
                    self.__reduced = redux
                except EEException as e:
                    raise ValidationError("Input dataset or toi is not valid")
        except ValueError as e:
            raise

    def filterGeometry(self, filter=None):
        """Filter by geometry

        Parameters
        ----------
        filter : ee.Geometry, optional
            Geometry object to filter collection's footprint
            (the default is None, which doesn't filter)

        Example
        -------
        >>c = GEEUtil('projects/fao-wapor/L1/L1_AETI_D')
        >>geojson = {
            "type": "Polygon",
            "coordinates": [
                [
                    [100, 0], [101, 0],
                    [101, 1], [100, 1],
                    [100, 0]
                ]
            ]
        }
        >>geom = Geometry()
        >>c.filterGeometry(filter=geom)

        """

        try:
            if filter and isinstance(filter, Geometry):
                try:
                    if not self.reduced:
                        redux = self.instance.filterBounds(filter).sort(
                            'system:time_start', True)
                    else:
                        redux = self.reduced.filterBounds(filter).sort(
                            'system:time_start', True)
                    self.__reduced = redux
                except EEException as e:
                    raise ValidationError("Input dataset or aoi is not valid")
        except ValueError as e:
            raise

    def getFootprint(self):
        """Return the footprint from the collection.

        Returns
        -------
        dict
            Footprint of all geometries from a collection
        """

        footprint = self.instance.geometry()
        return footprint.getInfo()

    def getBands(self):
        """Return the bands from the first image of the collection

        """

        bands = self.info()["features"][0]["bands"]
        return [band["id"] for band in bands]

    def is_reduced_empty(self):
        """Return if the reduced instance collection is empty

        Returns
        -------
        bool
            True/False if the filtered collection is empty
        """

        if self.reduced:
            try:
                if self.info(reduced=True)["features"]:
                    return False
                else:
                    return True
            except EEException as e:
                raise
        else:
            raise ValueError(
                "Calling function while the reduced doesn't exist"
            )

    def info(self, reduced=False):
        """Wrap earth engine getInfo operation

        Parameters
        ----------
        reduced : bool, optional
            Evaluate original or reduced instance
            (the default is False, which gives information of original asset)

        Returns
        -------
        dict
            All information of the asset collection

        """

        try:
            if reduced:
                try:
                    return self.reduced.getInfo()
                except AttributeError as e:
                    raise ValueError("Reduced instance collection doesn't exist yet")
            return self.instance.getInfo()
        except EEException as e:
            raise

    def mapUrl(self, reduced=False):
        """Wrap earth engine getMapId operation

        Parameters
        ----------
        reduced : bool, optional
            Evaluate original or reduced instance
            (the default is False, which gives map of original asset)

        Returns
        -------
        str
            URL of the tile service for the asset collection

        """

        try:
            if reduced:
                try:
                    return createInstanceUrl(self.reduced)
                except AttributeError as e:
                    raise ValueError(
                        "Reduced instance collection doesn't exist yet")
            return createInstanceUrl(self.instance)
        except EEException as e:
            raise

    def getStat(self, band=None, reduced=False):
        """Wrap earth engine aggregate_stats operation

        Parameters
        ----------
        band: str, optional
            Band of the collection
            (the default is None, which gives stat with first band of images)
        reduced: bool, optional
            Evaluate original or reduced instance
            (the default is False, which gives stat of original asset)

        Returns
        -------
        dict
            Dictionary of min, max, sum, mean for the asset collection

        """

        try:
            bands = self.getBands()
            if band and band not in bands:
                raise ValidationError("Provided band is not valid")
            else:
                band = bands[0]
            if reduced:
                try:
                    return createCollectionStat(self.reduced, band)
                except AttributeError as e:
                    raise ValueError(
                        "Reduced instance collection doesn't exist yet")
            return createCollectionStat(self.instance, band)
        except EEException as e:
            raise
