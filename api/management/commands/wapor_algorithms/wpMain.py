#! /usr/bin/env python
"""
    Main class for activating different calculations available in wpCalc.py via argparse
"""
import argparse
#import datetime
import logging
import sys
from wpCalc import L1WaterProductivity

# def valid_date(s):
#     try:
#         return datetime.datetime.strptime(s, "%Y-%m-%d").date()
#     except ValueError:
#         msg = "Not a valid date: '{0}'.".format(s)
#         raise argparse.ArgumentTypeError(msg)


def setup(args=None, parser=None):


    parser = argparse.ArgumentParser(description='Water Productivity using Google Earth Engine')

    parser.add_argument("timeframe",
                        nargs="*",
                        help="Calculate Water Productivity Annually for the chosen period"
                        )

    parser.add_argument('-x', '--export', choices=['u', 'd', 't'],
                        help="Choose export to url(-u), drive (-d) or asset (-t)")

    parser.add_argument('-i', '--map_id',
                        help="Generate map id for generating tiles",
                        action="store_true")

    parser.add_argument('-s', '--arealstat', #choices=['f', 'j'],
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

    # parser.add_argument("-v", "--verbose",
    #                     help="Increase output verbosity",
    #                     action="store_true")

    # return parser.parse_args()
    # print 'wpMainParser='+str(parser.parse_args())
    return parser


def run(results):

    logger = logging.getLogger("wpWin")
    logger.setLevel(level=logging.DEBUG)

    formatter = logging.Formatter("%(levelname) -4s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s")

    fh = logging.FileHandler('wapor.log')
    fh.setLevel(logging.ERROR)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # results = parser.parse_args()
    # logger.debug(results)

    args_list = {k: v for k, v in vars(results).items() if v is not None}
    logger.debug(args_list)
    logger.debug(len(args_list['timeframe']))

    # Metodo statico non devo inizializzare la classe molti saranno cosi alla fine
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

    if results.arealstat:
        if isinstance(results.arealstat, list):
            selection_country = results.arealstat[0]
        else:
            selection_country = results.arealstat
        country_stats = analysis_level_1.generate_areal_stats_fusion_tables(selection_country, wp_gb)
        if country_stats != 'no country':
            logger.debug("RESPONSE=%s" % country_stats)
        else:
            logger.debug("Country Error")
            logger.error("No country named {} in db".format(selection_country))

    if results.map_id:
        map_ids = {'agbp': agbp, 'eta': eta, 'wp_gross': wp_gb}
        logger.debug("RESULT=%s" % analysis_level_1.map_id_getter(**map_ids))

    # analysis_level_1.image_export(results.export, wp_gb)


if __name__ == '__main__':

    # Updated upstream
    results = setup().parse_args()
    run(results)
