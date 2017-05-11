#! /usr/bin/env python
# coding: utf-8
"""
    All calculation for Water Production biomass plus some additional features:

    1 - overlay map in a map viewer
    2 - generate a chart for each component used for calculating water productivity
    3 - generation of areal statistics (e.g. mean, max,etc...) for a country or river basin
    4 - generation of time-series for a specific collection of data stored in Google Earth Engine
    5 - export the calculated dataset in GDrive, GEE Asset, geoserver, etc...

"""

import ee
import time
# from ee import mapclient
import sys
import os
import glob
import datetime
# import pandas as pd
import logging

from osgeo import ogr


class WaterProductivityCalc(object):

    ee.Initialize()

    _REGION = [[-25.0, -37.0], [60.0, -41.0], [58.0, 39.0], [-31.0, 38.0], [-25.0, -37.0]]
    _COUNTRIES = ee.FeatureCollection('ft:1ZDEMjtnWm_smu7l_z3fx91BbxyCRzP2A3cEMrEiP')
    _WSHEDS = ee.FeatureCollection('ft:1IXfrLpTHX4dtdj1LcNXjJADBB-d93rkdJ9acSEWK')

    def __init__(self):
        pass


class L1WaterProductivity(WaterProductivityCalc):

    """
        Create Water Productivity raster file for annual and dekadal timeframes for Level 1 (Countries and Basins
    """

    _L1_RET_DAILY = ee.ImageCollection("projects/fao-wapor/L1_RET")
    _L1_PCP_DAILY = ee.ImageCollection("projects/fao-wapor/L1_PCP")
    _L1_NPP_DEKADAL = ee.ImageCollection("projects/fao-wapor/L1_NPP")
    _L1_AET_DEKADAL = ee.ImageCollection("projects/fao-wapor/L1_AET")
    _L1_TFRAC_DEKADAL = ee.ImageCollection("projects/fao-wapor/L1_TFRAC")

    def __init__(self):

        """ Constructor for date and dataset for WPgb"""

        self.L1_logger = logging.getLogger("wpWin.wpCalc")
        self.L1_AET_calc = self._L1_AET_DEKADAL
        self.L1_AGBP_calc = self._L1_NPP_DEKADAL

        AET_component_3dekad = ee.Image("projects/fao-wapor/L1_TFRAC/L1_TFRAC_1003")
        # Get scale (in meters) information from first image
        self.scale_calc = AET_component_3dekad.projection().nominalScale().getInfo()
        self.L1_logger.debug('Image scale %f ' % self.scale_calc)

    def date_selection(self, **kwargs):

        """ Modify date for selecting datasets to be used for WPgm"""

        self._date_start = str(kwargs.get('date_start'))
        self._date_end = str(kwargs.get('date_end'))

    def image_selection(self):

        """ Filter datasets selecting only images within the starting end ending date to be used for WPbm"""

        collection_agbp_filtered = L1WaterProductivity._L1_NPP_DEKADAL.filterDate(
            self._date_start,
            self._date_end)

        collection_aet_filtered = L1WaterProductivity._L1_AET_DEKADAL.filterDate(
            self._date_start,
            self._date_end)

        self.L1_AGBP_calc = collection_agbp_filtered
        self.L1_AET_calc = collection_aet_filtered

        agbp_num = collection_agbp_filtered.size().getInfo()
        aet_num = collection_aet_filtered.size().getInfo()

        self.L1_logger.debug("AGBP selected %d" % agbp_num)
        self.L1_logger.debug("AET selected %d" % aet_num)

        return self.L1_AGBP_calc, self.L1_AET_calc

    @property
    def multiply_npp(self, filtering_values):

        """ Sets the dataset to be used in conjunction with Actual Evapotranspiration for WPgb"""

        coll_npp_filtered = self._L1_NPP_DEKADAL.filterDate(
            self._date_start,
            self._date_end)
        coll_npp_multiplied = coll_npp_filtered.map(lambda npp_images: npp_images.multiply(filtering_values[0]))

        self.L1_AGBP_calc = coll_npp_multiplied

        return self.L1_AGBP_calc

    def agbp_aggregated(self):

        """Aggregate above ground biomass productivity for annual calculation or water productivity"""

        # the image.multiply(0.01444) multiplies all bands by 0.01444, including the days in dekad.
        # That is why the final WP values were so low...we should first multiply, then, in the same function, add the extra band
        def agbp_multiplication(image):
            img_multi = image.multiply(0.01444).addBands(image.metadata('days_in_dk'))
            return img_multi
        agbp_npp_multiplied = self.L1_AGBP_calc.map(agbp_multiplication)

        # get AGBP value, divide by 10 (as per FRAME spec) to get daily value, and multiply by number of days in dekad
        # we don't need to divide by 10 now: it was previously valid on sample data, and we don't use AGBP as input anyway.
        def npp_add_dk(image):
            mmdk = image.select('b1').multiply(image.select('days_in_dk'))
            return mmdk
        npp_with_dekad = agbp_npp_multiplied.map(npp_add_dk)

        aggregated_agbp = npp_with_dekad.reduce(ee.Reducer.sum())

        return aggregated_agbp

    def aet_aggregated(self):

        """Aggregate actual evapotranspiration for annual calculation or water productivity"""

        coll_aet_sorted = self.L1_AET_calc.sort('system:time_start', True)
        aggregated_aet = coll_aet_sorted.reduce(ee.Reducer.sum())

        return aggregated_aet

    def transpiration(self):

        """Aggregate transpiration using acttual evapotranspiration,above ground biomas productivity and t_fraction"""

        # This is calculated at class level for WPgb, WPnb
        # collAETFiltered = _L1_AET_DEKADAL.filterDate(start, end).sort('system:time_start', True)
        L1_TFRAC_calc = L1WaterProductivity._L1_TFRAC_DEKADAL.filterDate(self._date_start, self._date_end).sort('system:time_start', True)


        # JOINING TWO Collections - Start
        Join = ee.Join.inner()
        FilterOnStartTime = ee.Filter.equals(
            leftField='system:time_start',
            rightField='system:time_start'
        )

        TFRAC_AET_collection_Join = ee.ImageCollection(Join.apply(self.L1_AET_calc,
                                                                  L1_TFRAC_calc,
                                                                  FilterOnStartTime))
        self.L1_logger.debug("Joined collections %s", TFRAC_AET_collection_Join.getInfo())
        # JOINING TWO Collections - End

        def Tfrac_AETdk(image):
            image_aet = ee.Image(image.get("primary"))
            image_tfrac = ee.Image(image.get("secondary"))
            t_a = ((image_aet.select('b1').multiply(image_tfrac.select('b1').divide(100)))
                   .multiply(0.1)).multiply(ee.Number(image_aet.get('days_in_dk'))).float()
            return ee.Image(t_a)
        T_annual = TFRAC_AET_collection_Join.map(Tfrac_AETdk)

        SUM_TFRAC_annual = T_annual.reduce(ee.Reducer.sum()).toFloat()
        return SUM_TFRAC_annual

    def water_productivity_gross_biomass(self):

        """wp_gross_biomass calculation returns all intermediate results besides the final wp_gross_biomass"""

        # Multiplied for generating AGBP from NPP using the costant 0.144  CHANGED 0.0144 for Release 1
        npp_multiplied = self.L1_AGBP_calc.map(lambda lista: lista.multiply(0.01444).addBands(lista.metadata('days_in_dk')))

        # .multiply(10); the multiplier will need to be
        # applied on net FRAME delivery, not on sample dataset
        agbp = npp_multiplied.sum()

        # add image property (days in dekad) as band
        eta_dekad_added = self.L1_AET_calc.map(lambda imm_eta2: imm_eta2.addBands(
                                                 imm_eta2.metadata(
                                                 'days_in_dk')))

        # get ET value, divide by 10 (as per FRAME spec) to get daily
        # value, and  multiply by number of days in dekad summed annuallyS
        aet_dekad_multiplied = eta_dekad_added.map(lambda imm_eta3: imm_eta3.select('b1')
                                                   .divide(10)
                                                   .multiply(imm_eta3.select('days_in_dk'))).sum()

        # scale ETsum from mm/m² to m³/ha for WP calculation purposes
        eta = aet_dekad_multiplied.multiply(10)

        # calculate biomass water productivity and add to map
        wp_gross_biomass = agbp.divide(eta)

        return agbp, eta, wp_gross_biomass

    def water_productivity_net_biomass(self, L1_AGBP_calc, L1_AET_calc):

        """wp_net_biomass calculation returns all intermediate results besides the final wp_gross_biomass"""
        pass

    def map_id_getter(self, **outputs_id):

        """Generate a map id and a token for the calcualted WPbm raster file"""

        map_ids = {}
        for key, val in outputs_id.iteritems():
            map_id = val.getMapId()
            map_ids[key] = {}
            map_ids[key]['mapid'] = map_id['mapid']
            map_ids[key]['token'] = map_id['token']
            map_ids[key]['image'] = map_id['image'].getInfo()

        # tilepath = ee.data.getTileUrl(map_id, 1, 0, 1)
        # print tilepath
        # mappa = mapclient.MapClient()
        # mappa.addOverlay(mapclient.MakeOverlay(wpbm_calc.getMapId({'min': 0, 'max': 3000})))
        # mappa.centerMap(17.75, 10.14, 4)

        return map_ids

    @staticmethod
    def image_visualization(raster_name, raster_plot):

        """Output the calculated raster using a map vizualizer """

        VisPar_AGBPy = {"opacity": 0.85, "bands": "b1", "min": 0, "max": 180,
                       "palette": "f4ffd9,c8ef7e,87b332,566e1b",
                       "region": WaterProductivityCalc._REGION}

        VisPar_ETay = {"opacity": 1, "bands": "b1", "min": 0, "max": 2000,
                      "palette": "d4ffc6,beffed,79c1ff,3e539f",
                      "region": WaterProductivityCalc._REGION}

        VisPar_TFRAC = {"opacity": 1,  "bands": "b1_sum",
                        "max": 800, "palette": "fffcdb,b4ffa6,3eba70,195766",
                        "region": WaterProductivityCalc._REGION}

        VisPar_WPgb = {"opacity": 0.85, "bands": "b1", "max": 2000,
                      "palette": "bc170f,e97a1a,fff83a,9bff40,5cb326",
                      "region": WaterProductivityCalc._REGION}

        if raster_name == 'aet':
            legend = VisPar_ETay
        elif raster_name == 'agbp':
            legend = VisPar_AGBPy
        elif raster_name == 't_frac':
            legend = VisPar_TFRAC
        elif raster_name == 'wp_gb':
            legend = VisPar_WPgb
        elif raster_name == 'wp_nb':
            legend = VisPar_WPgb

        mapclient.addToMap(raster_plot, legend, raster_name)
        mapclient.centerMap(17.75, 10.14, 4)

    @staticmethod
    def generate_areal_stats_dekad_country(chosen_country, wbpm_calc):

        """Calculates several statistics for the Water Productivity calculated raster for a chosen country"""
        just_country = WaterProductivityCalc._COUNTRIES.filter(ee.Filter.eq('name', chosen_country))
        if just_country.size().getInfo() > 0:
            cut_poly = just_country.geometry()
            # print cut_poly.getInfo()
            raster_nominal_scale = wbpm_calc.projection().nominalScale().getInfo()

            means = wbpm_calc.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=cut_poly,
                scale=raster_nominal_scale,
                maxPixels=1e9
            )
            mean = means.getInfo()
            mean['mean'] = mean.pop('b1')

            reducers_min_max_sum = ee.Reducer.minMax().combine(
                reducer2=ee.Reducer.sum(),
                sharedInputs=True
            )

            # Use the combined reducer to get the min max and SD of the image.
            stats = wbpm_calc.reduceRegion(
                reducer=reducers_min_max_sum,
                bestEffort=True,
                geometry=cut_poly,
                scale=raster_nominal_scale
            )
            min_max_sum = stats.getInfo()

            # Display the dictionary of band means and SDs.
            min_max_sum['min'] = min_max_sum.pop('b1_min')
            min_max_sum['sum'] = min_max_sum.pop('b1_sum')
            min_max_sum['max'] = min_max_sum.pop('b1_max')
            min_max_sum.update(mean)
            return min_max_sum
        else:
            return 'no country'

    def generate_tiles(self):

        """INCOMPLETE  Split the calculated WPbm in 100 tiles facilitating the export"""

        driver = ogr.GetDriverByName('ESRI Shapefile')
        dir_shps = "tiles"
        os.chdir(dir_shps)
        file_shps = glob.glob("*.shp")

        allExportWPbm = []
        file_names = []

        for file_shp in file_shps:

            dataSource = driver.Open(file_shp, 0)

            if dataSource is None:
                sys.exit(('Could not open {0}.'.format(file_shp)))
            else:
                layer = dataSource.GetLayer(0)
                extent = layer.GetExtent()
                active_file = "tile_" + str(file_shp.split('.')[0]).split("_")[3]
                file_names.append(active_file)
                low_sx = extent[0], extent[3]
                up_sx = extent[0], extent[2]
                up_dx = extent[1], extent[2]
                low_dx = extent[1], extent[3]

                cut = [list(low_sx), list(up_sx), list(up_dx), list(low_dx)]

                Export_WPbm = {
                    "crs": "EPSG:4326",
                    "scale": 250,
                    'region': cut}
                allExportWPbm.append(Export_WPbm)

        return allExportWPbm, file_names

    def image_export(self, exp_type, wpgb):

        """ INCOMPLETE Export the 72 of the calculated wpgb to Google Drive,
        GEE Asset or generating a url for each tile"""

        driver = ogr.GetDriverByName('ESRI Shapefile')
        dir_shps = "tiles"
        os.chdir(dir_shps)
        list_shps = glob.glob("*.shp")

        for file_shp in list_shps:
            dataSource = driver.Open(file_shp, 0)
            if dataSource is None:
                sys.exit(('Could not open {0}.'.format(file_shp)))
            else:
                layer = dataSource.GetLayer(0)
                extent = layer.GetExtent()
                active_file = str(file_shp.split('.')[0])
                low_sx = extent[0], extent[3]
                up_sx = extent[0], extent[2]
                up_dx = extent[1], extent[2]
                low_dx = extent[1], extent[3]

                cut = []
                cut = [list(low_sx), list(up_sx), list(up_dx), list(low_dx)]

                Export_WPbm = {
                    "crs": "EPSG:4326",
                    "scale": 250,
                    'region': cut}

                if exp_type == 'u':
                    list_of_downloading_urls = []
                    try:
                        url_WPbm = wpgb.getDownloadUrl(Export_WPbm)
                        list_of_downloading_urls.append(url_WPbm)
                    except:
                        self.L1_logger.error("Unexpected error:", sys.exc_info()[0])
                        raise
                elif exp_type == 'd':
                    task = ee.batch.Export.image(wpgb,
                                                 active_file,
                                                 Export_WPbm)
                    task.start()
                    while task.status()['state'] == 'RUNNING':
                        # Perhaps task.cancel() at some point.
                        time.sleep(1)
                    self.L1_logger.info('Done.', task.status())

                elif exp_type == 'a':
                    active_file = "tile_" + str(file_shp.split('.')[0]).split("_")[3]
                    asset_temp = "projects/fao-wapor/testExpPython/JanMar2015/" + active_file
                    ee.batch.Export.image.toAsset(
                        image=wpgb,
                        description=active_file,
                        assetId=asset_temp,
                        crs="EPSG:4326",
                        scale= 250,
                        region=cut
                        ).start()

                elif exp_type == 'n':
                    print("Nothing yet")
                    pass
