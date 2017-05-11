#! /usr/bin/env python
"""
    Main class for activating different calculations available in wpCalc.py via argparse
"""
import argparse
import datetime
import logging

from wpCalc import L1WaterProductivity


def valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)

def main(args=None):

    logger = logging.getLogger("wpWin")
    logger.setLevel(level=logging.DEBUG)

    formatter = logging.Formatter("%(levelname) -4s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s")

    fh = logging.FileHandler('wapor.log')
    fh.setLevel(logging.ERROR)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

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

    parser.add_argument('-s', '--arealstat',
                        help="Zonal statistics form a WaterProductivity generated in GEE for the chosen country")

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

    parser.add_argument("-v", "--verbose",
                        help="Increase output verbosity",
                        action="store_true")

    results = parser.parse_args()

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
        logger.debug("CHOSEN DATASET %s " % results.aggregation)
        if results.aggregation == 'aet':
            eta = analysis_level_1.aet_aggregated()
        if results.aggregation == 'agbp':
            agbp = analysis_level_1.agbp_aggregated()
        if results.aggregation == 'wp_gb':
            agbp, eta, wp_gb = analysis_level_1.water_productivity_gross_biomass()
        if results.aggregation == 't_frac':
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
        country_stats = analysis_level_1.generate_areal_stats_dekad_country(results.arealstat, wp_gb)
        if country_stats != 'no country':
            logger.debug(country_stats)
        else:
            logger.debug("Country Error")
            logger.error("No country named {} in db".format(results.arealstat))

    if results.map_id:
        map_ids = {'agbp': agbp, 'eta': eta, 'wp_gross': wp_gb}
        logger.debug(analysis_level_1.map_id_getter(**map_ids))

    # analysis_level_1.image_export(results.export, wp_gb)

if __name__ == '__main__':
    main()
