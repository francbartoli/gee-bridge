# coding: utf-8
"""
    All calculation for Water Production biomass plus some additional features:

    1 - overlay map in a map viewer
    2 - generate a chart for each componenet used for calculating sater productivity
    3 - generation of areal statistics (e.g. mean, max,etc...) for a country or river basin
    4 - generation of timeseries for a specific collection of data stored in Google Earth Engine
    5 - export the calculated dataset in GDrive, GEE Asset, geoserver, etc...

"""

import ee
import time
# import ee.mapclient
# import matplotlib.pyplot as plt
import sys
from osgeo import ogr
import os
import glob
import datetime
from mycustomdjango import settings
# import seaborn

class WaterProductivityCalc(object):

    def __init__(self):
        pass

class L1WaterProductivity(WaterProductivityCalc):

    """
        Create Water Productivity raster file for annual and dekadal timeframes for Level 1 (Countries and Basins
    """

    def __init__(self):

        ee.Initialize(settings.EE_CREDENTIALS)

        self._REGION = [[-25.0, -37.0], [60.0, -41.0], [58.0, 39.0], [-31.0, 38.0],  [-25.0, -37.0]]

        self.countries = ee.FeatureCollection('ft:1tdSwUL7MVpOauSgRzqVTOwdfy17KDbw-1d9omPw')
        self.wsheds = ee.FeatureCollection('ft:1IXfrLpTHX4dtdj1LcNXjJADBB-d93rkdJ9acSEWK')

        self._L1_AGBP_SEASONAL = ee.ImageCollection("projects/fao-wapor/L1_AGBP")
        self._L1_AGBP_DEKADAL = ee.ImageCollection("projects/fao-wapor/L1_AGBP250")
        self._L1_ETa_DEKADAL = ee.ImageCollection("projects/fao-wapor/L1_AET")
        self._L1_AET250 = ee.ImageCollection("users/lpeiserfao/AET250")
        self._L1_NPP_DEKADAL = ee.ImageCollection("projects/fao-wapor/L1_NPP250")

        self.l1_AGBP_calc = self._L1_AGBP_SEASONAL
        self.l1_AET250_calc = self._L1_AET250
        self.l1_NPP250_calc = self._L1_NPP_DEKADAL

        self.VisPar_AGBPy = {"opacity": 0.85, "bands": "b1",
                             "min": 0, "max": 12000,
                             "palette": "f4ffd9,c8ef7e,87b332,566e1b",
                             "region": self._REGION}

        self.VisPar_ETay = {"opacity": 1, "bands": "b1",
                            "min": 0, "max": 2000,
                            "palette": "d4ffc6,beffed,79c1ff,3e539f",
                            "region": self._REGION}

        self.VisPar_WPbm = {"opacity": 0.85, "bands": "b1",
                            "min": 0, "max": 1.2,
                            "palette": "bc170f,e97a1a,fff83a,9bff40,5cb326",
                            "region": self._REGION}

    @property
    def multiply_npp(self):
        """ Returns the dataset to be used in conjunction with Actual Evapotranspiration for WPbm"""
        return self.l1_NPP250_calc

    @multiply_npp.setter
    def multiply_npp(self, valori_filtro):
        """ Sets the dataset to be used in conjunction with Actual Evapotranspiration for WPbm"""

        data_start = str(valori_filtro[1])
        data_end = str(valori_filtro[2])

        coll_npp_filtered = self._L1_NPP_DEKADAL.filterDate(
            data_start,
            data_end)
        coll_npp_multiplied = coll_npp_filtered.map(lambda immagini: immagini.multiply(valori_filtro[0]))

        self.l1_NPP250_calc = coll_npp_multiplied


    @property
    def image_selection(self):
        """ Returns both datasets to be used for WPbm"""
        return self.l1_AGBP_calc, self.l1_AET250_calc

    @image_selection.setter
    def image_selection(self, date_p):

        """ Filter datasets selecting only images within the starting end ending date to be used for WPbm"""

        data_start = str(date_p[0])
        data_end = str(date_p[1])

        collection_agbp_filtered = self._L1_AGBP_DEKADAL.filterDate(
            data_start,
            data_end)

        collection_aet_filtered = self._L1_AET250.filterDate(
            data_start,
            data_end)

        self.l1_AGBP_calc = collection_agbp_filtered
        self.l1_AET250_calc = collection_aet_filtered

    def image_processing(self, L1_AGBP_calc, L1_AET_calc):

        """WPbm calculation returns all intermediate results besides the final WPbm"""

        # Above Ground Biomass Production with masked NoData (pixel < 0)
        L1_AGBP_masked = L1_AGBP_calc.map(lambda lista: lista.updateMask(lista.gte(0)))
        # .multiply(10); the multiplier will need to be
        # applied on net FRAME delivery, not on sample dataset
        L1_AGBP_summed = L1_AGBP_masked.sum()
        
        # Actual Evapotranspiration with valid ETa values (>0 and <254)
        ETaColl1 = L1_AET_calc.map(lambda imm_eta: imm_eta.updateMask
                                   (imm_eta.lt(254) and (imm_eta.gt(0))))

        # add image property (days in dekad) as band
        ETaColl2 = ETaColl1.map(lambda imm_eta2: imm_eta2.addBands(
                                                 imm_eta2.metadata(
                                                 'days_in_dk')))        
        
        # get ET value, divide by 10 (as per FRAME spec) to get daily
        # value, and  multiply by number of days in dekad summed annuallyS
        ETaColl3 = ETaColl2.map(lambda imm_eta3: imm_eta3.select(
            'b1').divide(10).multiply(imm_eta3.select('days_in_dk'))).sum()

        # scale ETsum from mm/m² to m³/ha for WP calculation purposes
        ETaTotm3 = ETaColl3.multiply(10)

        # calculate biomass water productivity and add to map
        WPbm = L1_AGBP_summed.divide(ETaTotm3)

        return L1_AGBP_summed, ETaColl1, ETaColl2, ETaColl3, WPbm

    def map_id_getter(self, wpbm_calc):

        """Generate a map id and a token for the calcualted WPbm raster file"""

        map_id = wpbm_calc.getMapId(self.VisPar_WPbm)
        info = wpbm_calc.getInfo()
        # return  values of map_id, token and general info
        values = {
            'mapid': map_id['mapid'],
            'token': map_id['token'],
            'image': info
        }
        return values

    def generate_ts(self, paese, data_start, data_end,dataset):

        """Generate a chart with the mean values calculated for a chosen country"""

        if dataset == 'agbp':
            collection = self._L1_AGBP_DEKADAL
        elif dataset == 'eta':
            collection = self._L1_ETa_DEKADAL
        elif dataset == 'aet':
            collection = self._L1_AET250
        elif dataset == 'npp':
            collection = self._L1_NPP_DEKADAL

        just_country = self.countries.filter(ee.Filter.eq('Country', paese))
        cut_poly = just_country.geometry()
        cut_bounding_box = cut_poly.bounds(1)

        collection_filtered = collection.filterDate(data_start, data_end).filterBounds(cut_bounding_box)

        def getMean(img):
            return img.reduceRegions(cut_bounding_box,
                                     ee.Reducer.mean(),
                                     200)

        ans = ee.FeatureCollection(collection_filtered.map(getMean)).flatten().aggregate_array('.all').getInfo()

        x_agbp = [x['properties']['mean'] for x in ans]
        labels_agbp = [x['id'][:8] for x in ans]
        lables_data = [datetime.datetime.strptime(label, "%Y%m%d").strftime('%Y-%m-%d') for label in labels_agbp]

        # plt.plot(x_agbp)
        # plt.title("timeserie")
        # plt.xticks(range(len(labels_agbp)), lables_data, rotation=60)
        # plt.show()

    def generate_areal_stats(self, paese, wbpm_calc):

        """Calculates several statistics for the Water Productivity calculated raster for a chosen country"""

        just_country = self.countries.filter(ee.Filter.eq('Country', paese))
        cut_poly = just_country.geometry()
        scala = wbpm_calc.projection().nominalScale().getInfo()

        country_mean = wbpm_calc.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=cut_poly,
            scale=scala,
            maxPixels=1e9
        )
        mean = country_mean.getInfo()
        mean['mean'] = mean.pop('b1')

        reducers = ee.Reducer.minMax().combine(
            reducer2=ee.Reducer.stdDev(),
            sharedInputs=True
        )

        # Use the combined reducer to get the min max and SD of the image.
        stats = wbpm_calc.reduceRegion(
            reducer=reducers,
            bestEffort=True,
            geometry=cut_poly,
            scale=scala,
        )

        # Display the dictionary of band means and SDs.
        min_max_std = stats.getInfo()
        min_max_std['min'] = min_max_std.pop('b1_min')
        min_max_std['std'] = min_max_std.pop('b1_stdDev')
        min_max_std['max'] = min_max_std.pop('b1_max')

        min_max_std.update(mean)

        return min_max_std


    def image_visualization(self, viz_type, L1_AGBP, ETaColl3, WPbm):

        """Output the calculated WPbm using a map vizualizer or a chart (in this case
        every componeent of the calculation is plotted """

        if viz_type == 'm':

            pass
            # ee.mapclient.addToMap(WPbm, self.VisPar_WPbm, 'Annual biomass water productivity')
            # ee.mapclient.centerMap(17.75, 10.14, 4)

        elif viz_type == 'c':

            url_thumb_AGBP = L1_AGBP.getThumbUrl(self.VisPar_AGBPy)
            # thumb_imag_AGBP = plt.imread(url_thumb_AGBP)

            url_thumb_ETaColl3 = ETaColl3.getThumbUrl(self.VisPar_ETay)
            # thumb_imag_ETaColl3 = plt.imread(url_thumb_ETaColl3)

            url_thumb_WPbm = WPbm.getThumbUrl(self.VisPar_WPbm)
            # thumb_imag_WPbm = plt.imread(url_thumb_WPbm)

            # fig = plt.figure()
            # ax1 = fig.add_subplot(2, 2, 1)
            # ax1.imshow(thumb_imag_AGBP)
            # ax1.set_title('AGBP')
            # ax1.axis('off')

            # ax2 = fig.add_subplot(2, 2, 2)
            # ax2.imshow(thumb_imag_ETaColl3)
            # ax2.set_title('ETaColl3')
            # ax2.axis('off')

            # ax3 = fig.add_subplot(2, 2, 3)
            # ax3.imshow(thumb_imag_WPbm)
            # ax3.set_title('WPbm')
            # ax3.axis('off')

            # plt.show()

    def generate_tiles(self):

        """INCOMPLETE  Split the calculated WPbm in 72 tiles facilitating the export"""

        driver = ogr.GetDriverByName('ESRI Shapefile')
        dir_shps = "/media/sf_Fabio/Downloads/water productivity/data/tiles/tiles10_touch/tiles"
        os.chdir(dir_shps)
        file_shps = glob.glob("*.shp")

        allExportWPbm = []
        nomi_files = []

        for file_shp in file_shps:

            dataSource = driver.Open(file_shp, 0)

            if dataSource is None:
                sys.exit(('Could not open {0}.'.format(file_shp)))
            else:
                layer = dataSource.GetLayer(0)
                extent = layer.GetExtent()
                nome_file = "tile_" + str(file_shp.split('.')[0]).split("_")[3]
                nomi_files.append(nome_file)
                primo = extent[0], extent[3]
                secondo = extent[0], extent[2]
                terzo = extent[1], extent[2]
                quarto = extent[1], extent[3]

                cut = []
                cut.append(list(primo))
                cut.append(list(secondo))
                cut.append(list(terzo))
                cut.append(list(quarto))

                Export_WPbm = {
                    "crs": "EPSG:4326",
                    "scale": 250,
                    'region': cut}
                allExportWPbm.append(Export_WPbm)

        return allExportWPbm, nomi_files


    def image_export(self, exp_type, WPbm):

        """ INCOMPLETE Export the 72 of the calculated WPbm to Google Drive,
        GEE Asset or generating a url for each tile"""

        driver = ogr.GetDriverByName('ESRI Shapefile')
        dir_shps = settings.SHAPEFILE_DIR
        os.chdir(dir_shps)
        file_shps = glob.glob("*.shp")

        for file_shp in file_shps:
            dataSource = driver.Open(file_shp, 0)
            if dataSource is None:
                sys.exit(('Could not open {0}.'.format(file_shp)))
            else:
                layer = dataSource.GetLayer(0)
                extent = layer.GetExtent()
                nome_file = str(file_shp.split('.')[0])
                primo = extent[0], extent[3]
                secondo = extent[0], extent[2]
                terzo = extent[1], extent[2]
                quarto = extent[1], extent[3]

                cut = []
                cut.append(list(primo))
                cut.append(list(secondo))
                cut.append(list(terzo))
                cut.append(list(quarto))

                Export_WPbm = {
                    "crs": "EPSG:4326",
                    "scale": 250,
                    'region': cut}

                if exp_type == 'u':
                    lista_url = []
                    try:
                        url_WPbm = WPbm.getDownloadUrl(Export_WPbm)
                        lista_url.append(url_WPbm)
                    except:
                        print("Unexpected error:", sys.exc_info()[0])
                        raise
                elif exp_type == 'd':
                    task = ee.batch.Export.image(WPbm,
                                                 nome_file,
                                                 Export_WPbm)
                    task.start()
                    while task.status()['state'] == 'RUNNING':
                        print 'Running'
                        # Perhaps task.cancel() at some point.
                        time.sleep(1)
                    print 'Done.', task.status()

                elif exp_type == 'a':
                    nome_file = "tile_" + str(file_shp.split('.')[0]).split("_")[3]
                    asset_temp = "projects/fao-wapor/testExpPython/JanMar2015/" + nome_file
                    ee.batch.Export.image.toAsset(
                        image=WPbm,
                        description=nome_file,
                        assetId=asset_temp,
                        crs="EPSG:4326",
                        scale= 250,
                        region=cut
                        ).start()

                elif exp_type == 'g':
                    nome_file = "tile_" + str(file_shp.split('.')[0]).split("_")[3]
                    asset_temp = "projects/fao-wapor/testExpPython/" + nome_file
                    print nome_file,asset_temp
                elif exp_type == 'n':
                    print("Nothing yet")
                    pass
