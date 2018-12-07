import logging
from api.utils.geo import GeoJsonUtil
from api.utils.gee import (
    GEEUtil,
    Collection,
    createImageStat,
    createInstanceUrl
)
from api.utils.map import Map, MapUtil
from api.utils.stat import Stat, StatUtil
from geojson.geometry import Polygon
from ee import Filter, DateRange, Geometry
from rest_framework.serializers import ValidationError


class UDWP:

    def __init__(self, **kwargs):

        self.logger = logging.getLogger(__name__)
        self.__name = "UDWP"
        self.logger.debug("Received kwargs are:\n{}".format(kwargs))

        # internal inputs
        self.__npp = Collection(name="NPP", id="", metadata={}, bands=[])
        self.__aeti = Collection(name="AETI", id="", metadata={}, bands=[])
        try:
            if kwargs["inputs"]:
                for input in kwargs["inputs"]:
                    if "NPP" in input["dataset"]:
                        self.__npp = self.__npp._replace(
                            id=input["dataset"]
                        )
                        self.__npp = self.__npp._replace(
                            metadata=input["metadata"]
                        )
                        self.__npp = self.__npp._replace(
                            bands=input["bands"]
                        )
                    elif "AETI" in input["dataset"]:
                        self.__aeti = self.__aeti._replace(
                            id=input["dataset"]
                        )
                        self.__aeti = self.__aeti._replace(
                            metadata=input["metadata"]
                        )
                        self.__aeti = self.__aeti._replace(
                            bands=input["bands"]
                        )
                    else:
                        raise ValidationError(
                            "\
Input datasets are not valid for Water Productivity"
                        )
        except KeyError as e:
            self.logger.exception("KeyError exception")
            raise ValidationError(
                "Input datasets are not valid for Water Productivity"
            )

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
                                "Area of interest is not valid"
                            )
                    # extract temporal filter and add it
                    if filter_k == "temporal_extent":
                        self.__filters['{}'.format(filter_k)] = filter_v
        except KeyError as e:
            self.logger.exception("KeyError exception")
            raise ValidationError("Area of interest is not valid")

        self.__outputs = {"maps": {}, "stats": {}, "tasks": {}}
        # FIXME into marmee so we can initialize self.__errors as {}
        self.__errors = {}

    @property
    def outputs(self):
        return self.__outputs

    @property
    def filters(self):
        return self.__filters

    @property
    def errors(self):
        return self.__errors

    # setters
    @outputs.setter
    def outputs(self, value):
        """Sets new value for attribute outputs

        Parameters
        ----------
        value: string
            Assign new outputs to instance

        """
        self.__outputs = value

    @filters.setter
    def filters(self, value):
        """Sets new value for attribute filters

        Parameters
        ----------
        value: string
            Assign new filters to instance

        """
        self.__filters = value

    @errors.setter
    def errors(self, value):
        """Sets new value for attribute errors

        Parameters
        ----------
        value: string
            Assign new errors to instance

        """
        self.__errors = value

    def execute(self):

        # utils
        m = MapUtil()
        s = StatUtil()

        # instantiate filters
        t_filter = Filter(
            DateRange(
                self.filters["temporal_extent"]["startdate"],
                self.filters["temporal_extent"]["enddate"]
            )
        )
        g_filter = Geometry(
            self.filters["spatial_extent"]
        )

        # instantiate input collections
        coll_aeti = GEEUtil(self.__aeti.id)
        coll_npp = GEEUtil(self.__npp.id)

        # reduce input collections with filters
        # AETI
        coll_aeti.filterDateRange(filter=t_filter)
        coll_aeti.filterGeometry(filter=g_filter)
        m_aeti = Map(
            name="{}-{}".format(coll_aeti.collection, "filtered"),
            rel=coll_aeti.collection,
            url=coll_aeti.mapUrl(reduced=True)
        )
        m.add_map(m_aeti)
        s_aeti = Stat(
            name="{}-{}".format(coll_aeti.collection, "filtered"),
            rel=coll_aeti.collection,
            stat=coll_aeti.getStat(reduced=True))
        s.add_stat(s_aeti)

        # NPP
        coll_npp.filterDateRange(filter=t_filter)
        coll_npp.filterGeometry(filter=g_filter)
        m_npp = Map(
            name="{}-{}".format(coll_npp.collection, "filtered"),
            rel=coll_npp.collection,
            url=coll_npp.mapUrl(reduced=True))
        m.add_map(m_npp)
        s_npp = Stat(
            name="{}-{}".format(coll_npp.collection, "filtered"),
            rel=coll_npp.collection,
            stat=coll_npp.getStat(reduced=True))
        s.add_stat(s_npp)

        # AGBP
        coll_npp2agbp = coll_npp.reduced.map(
            lambda image: image.multiply(0.01444).addBands(
                image.metadata("n_days_extent")
            )
        )

        coll_agbp_dk = coll_npp2agbp.map(
            lambda image: image.select("b1").multiply(
                image.select("n_days_extent")
            )
        ).sum()

        # ETA
        coll_eta = coll_aeti.reduced.map(
            lambda image: image.addBands(image.metadata("n_days_extent"))
        )
        coll_eta_dk = coll_eta.map(
            lambda image: image.select("b1").multiply(
                image.select("n_days_extent")
            )
        ).sum()

        # WPBM
        wpbm = coll_agbp_dk.divide(coll_eta_dk)
        # print("wpbm={}".format(wpbm.getInfo()))
        m_wpbm = Map(
            name="{}-{}".format("WPBM", "calculated"),
            rel="WPBM",
            url=createInstanceUrl(wpbm))
        m.add_map(m_wpbm)
        s_wpbm = Stat(
            name="{}-{}".format("WPBM", "calculated"),
            rel="WPBM",
            stat=createImageStat(img_inst=wpbm, region=g_filter, band="b1"))
        s.add_stat(s_wpbm)
        # print("stats={}".format(createImageStat(img_inst=wpbm, region=g_filter, band="b1")))

        self.__outputs["maps"] = m.maps
        self.__outputs["stats"] = s.stats

        return {"outputs": self.outputs, "errors": self.errors}

    def is_polygon(self, obj):
        """Retrieve if the spatial extent is of polygon type"""

        type = GeoJsonUtil(obj).type
        self.logger.debug("GeoJSON type is {}".format(type))
        if type is not Polygon:
            return False
        else:
            return True
