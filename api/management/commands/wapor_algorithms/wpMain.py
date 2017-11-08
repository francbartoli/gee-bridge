#! /usr/bin/env python
"""
Main class for activating different calculations available in wpCalc.py via argparse
"""
import argparse
import getpass
import logging
import os
import sys

import wpDataManagement as dm
from wpCalc import L1WaterProductivity


def setup(args=None, parser=None):
    """Summary

    Args:
        args (None, optional): Description
        parser (None, optional): Description

    Returns:
        TYPE: Description
    """
    parser = argparse.ArgumentParser(
        description='Water Productivity using Google Earth Engine')

    parser.add_argument("timeframe",
                        nargs="*",
                        help="Calculate Water Productivity Annually for the chosen period"
                        )

    parser.add_argument('-x', '--export', choices=['u', 'd', 't'],
                        help="Choose export to url(-u), drive (-d) or asset (-t)")

    parser.add_argument('-i', '--map_id',
                        help="Generate map id for generating tiles",
                        action="store_true")

    parser.add_argument('-s', '--arealstat',
                        choices=['c', 'w', 'g'],
                        nargs=argparse.REMAINDER,
                        help="Zonal statistics form a WaterProductivity generated in GEE "
                        "for the chosen Country/Watershed or User Defined Area")

    parser.add_argument('-o', '--output',
                        choices=['csv', 'json'],
                        help="Choose format fo the annual statistics csv(-o 'csv') or json (-o 'json')")

    parser.add_argument("-a",
                        "--aggregation",
                        choices=['agbp', 'aet', 't_frac', 'wp_gb', 'wp_nb'],
                        help="Aggregate dekadal data at annual level"
                        )

    parser.add_argument("-m",
                        "--map",
                        choices=['agbp', 'aet', 't_frac', 'wp_gb', 'wp_nb'],
                        help="Show calculated output overlaid on Google Map"
                        )

    parser.add_argument("-u",
                        "--upload",
                        type=str,
                        help="Upload or update data in Google Earth Engine"
                        )

    # parser.add_argument("-v", "--verbose",
    #                     help="Increase output verbosity",
    #                     action="store_true")

    return parser


def run(results):
    """Summary

    Args:
        results (TYPE): Description
    """
    logger = logging.getLogger("wpWin")
    logger.setLevel(level=logging.DEBUG)

    formatter = logging.Formatter(
        "%(levelname) -4s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s")

    fh = logging.FileHandler('wapor.log')
    fh.setLevel(logging.ERROR)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    args_list = {k: v for k, v in vars(results).items() if v is not None}
    # logger.debug(len(args_list['timeframe']))

    # def methods(**kwargs):
    #     print kwargs
    # methods(**vars(results))

    # Static method many will be similar to reduce the verbosity of the code
    # print L1WaterProductivity.water_productivity_net_biomass_pre_calculated_annual_values(2010)

    analysis_level_1 = L1WaterProductivity()

    if len(results.timeframe) == 1:
        input_year = str(results.timeframe[0])
        date_start = input_year + '-01-01'
        date_end = input_year + '-12-31'
    elif len(results.timeframe) == 2:
        date_start = results.timeframe[0]
        date_end = results.timeframe[1]
    else:
        print("date error")
        pass

    selection_params = {'date_start': date_start, 'date_end': date_end}
    logger.debug(selection_params)
    analysis_level_1.date_selection(**selection_params)
    analysis_level_1.image_selection()

    if results.aggregation:
        if isinstance(results.aggregation, list):
            selection_aggregation = results.aggregation[0]
        else:
            selection_aggregation = results.aggregation
        logger.debug("Working on %s " % selection_aggregation)
        if selection_aggregation == 'aet':
            eta = analysis_level_1.aet_aggregated()
        if selection_aggregation == 'agbp':
            agbp = analysis_level_1.agbp_aggregated()
        if selection_aggregation == 'wp_gb':
            agbp, eta, wp_gb = analysis_level_1.water_productivity_gross_biomass()
        if selection_aggregation == 't_frac':
            eta = analysis_level_1.aet_aggregated()
            t_frac = analysis_level_1.transpiration()

    if results.map:
        if results.map == 'aet':
            analysis_level_1.image_visualization(results.map, eta)
        if results.map == 'agbp':
            analysis_level_1.image_visualization(results.map, agbp)
        if results.map == 'wp_gb':
            analysis_level_1.image_visualization(results.map, wp_gb)
        if results.map == 't_frac':
            analysis_level_1.image_visualization(results.map, t_frac)

    if isinstance(results.arealstat, list):

        try:
            area_stats = analysis_level_1.generate_areal_stats(
                results.arealstat[0], results.arealstat[1], wp_gb)
            logger.debug("RESPONSE=%s" % area_stats)

        except Exception as e:
            if isinstance(e, UnboundLocalError):
                logger.debug("WP_GP aggregation Error")
                logger.error("ERRORS={}".format(e))
            elif results.arealstat[0] == 'c':
                logger.debug("Country Error")
                logger.error("ERRORS=No country named {} in db".format(
                    results.arealstat[1]))
            elif results.arealstat[0] == 'w':
                logger.debug("Watershed Error")
                logger.error("ERRORS=No watershed named {} in db".format(
                    results.arealstat[1]))
            elif results.arealstat[0] == 'g':
                logger.debug("User Defined Area format Error")
                logger.error("ERRORS=Invalid GeoJson {} to parse".format(
                    results.arealstat[1]))

    else:

        logger.debug("ERRORS=Invalid arealstat arguments {} format".format(
            results.arealstat
        ))

    if results.map_id:
        map_ids = {'agbp': agbp, 'eta': eta, 'wp_gross': wp_gb}
        logger.debug("RESULT=%s" % analysis_level_1.map_id_getter(**map_ids))

    if results.upload:

        properties = None
        no_data = None

        username_gee = raw_input('Please enter a valid GEE User Name: ')
        password_gee = getpass.getpass('Please Enter a valid GEE Password: ')
        data_management_session = dm.DataManagement(username_gee, password_gee)
        active_session = data_management_session.create_google_session()
        upload_url = data_management_session.get_upload_url(active_session)

        files_repo = str(results.upload)
        try:
            logger.debug("File %s found" % files_repo)
            if os.path.isfile(files_repo):
                gee_asset = '_'.join(files_repo.split('/')[-1].split("_")[0:2])
                # gee_file = files_repo.split ( '/' )[-1].split ( "." )[0]
                present_assets = data_management_session.get_assets_info(
                    gee_asset)
                data_management_session.data_management(active_session,
                                                        upload_url,
                                                        present_assets,
                                                        files_repo,
                                                        properties,
                                                        no_data)
            elif os.path.isdir(files_repo):
                new_files = []
                root_dir = None
                for (dirpath, dirnames, filenames) in os.walk(files_repo):
                    new_files.extend(filenames)
                    root_dir = dirpath
                    break

                for each_file in new_files:
                    file_temp = root_dir + "/" + each_file
                    gee_asset = '_'.join(each_file.split("_")[0:2])
                    # gee_file = each_file.split ( "." )[0]
                    present_assets = data_management_session.get_assets_info(
                        gee_asset)
                    data_management_session.data_management(active_session,
                                                            upload_url,
                                                            present_assets,
                                                            file_temp,
                                                            properties,
                                                            no_data)
        except:
            logger.error("ERRORS=File %s not found" % files_repo)

    args = {k: v for k, v in vars(results).items() if v is not None}
    logger.debug("Final Check %s" % args)
    # analysis_level_1.image_export(results.export, wp_gb)


if __name__ == '__main__':

    # Updated upstream
    results = setup().parse_args()

    run(results)
