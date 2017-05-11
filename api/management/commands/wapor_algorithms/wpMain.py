"""
    Main class for activating different calculations available in wpCalc.py via argparse
"""
import argparse
import datetime


from wpCalc import L1WaterProductivity


def valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def main(args=None):

    # import ipdb; ipdb.set_trace()
    parser = argparse.ArgumentParser(description='Water Productivity using Google Earth Engine')
    groupTimePeriod = parser.add_mutually_exclusive_group()
    groupTimePeriod.add_argument("-a",
                                 "--annual",
                                 metavar='Year',
                                 type=int,
                                 help="Calculate Water Productivity Annually"
                                      " - Year must be provided",
                                 default=0)

    groupTimePeriod.add_argument("-d",
                                 "--dekadal",
                                 metavar="Start End Dates",
                                 help="Calculate Water Productivity for dekads"
                                      " - Starting and ending date must"
                                      " be provided with the following "
                                      "format YYYY-MM-DD",
                                 nargs=2,
                                 type=valid_date)

    group_output = parser.add_mutually_exclusive_group()
    group_output.add_argument("-c",
                              "--chart",
                              help="Each calculated component (AGBP, AET, WPm)"
                                   " shown on a chart",
                              action="store_true")
    group_output.add_argument("-m",
                              "--map",
                              help="Show the final output overlaid "
                                   " on Google Map",
                              action="store_true")

    parser.add_argument('-e', '--export', choices=['u', 'd', 'a', 'g', 'n'],
                        help="Choose export to url(-u), drive (-d), "
                             " asset (-t) or geoserver (-g)")

    parser.add_argument('-i', '--map_id',
                        help="Generate map id for generating tiles",
                        action="store_true")

    parser.add_argument('-r', '--replace', type=float,
                        help="Replace the Above Ground Biomass Production with Net Primary Productivity multiplied "
                             "by a constant value. Sending -r 1.25 will set agbp=npp * 1.25. If not provided default "
                             "datasets will be used instead")

    parser.add_argument('-t', '--timeseries',
                        choices=['agbp', 'eta', 'aet', 'npp'],
                        help="Time Series from data collections stored in GEE for the chosen country/dataset",
                        default=None)

    parser.add_argument('-s', '--arealstat',
                        help="Zonal statistics form a WaterProductivity layer generated on the fly in GEE for the chosen country")

    parser.add_argument("-vv", "--verbose",
                        help="Increase output verbosity",
                        action="store_true")

    # results = parser.parse_args()
    # return results
    return parser.parse_args()


def run(results):
    elaborazione = L1WaterProductivity()
    # import ipdb; ipdb.set_trace()
    if results['annual']:
        abpm, aet = elaborazione.image_selection
    elif results['dekadal']:
        date_v = [results['dekadal'][0], results['dekadal'][1]]
        elaborazione.image_selection = date_v
        abpm, aet = elaborazione.image_selection

    if results['replace']:
        moltiplicatore = results['replace']
        filtri = [moltiplicatore, results['dekadal'][0], results['dekadal'][1]]
        elaborazione.multiply_npp = filtri
        abpm = elaborazione.multiply_npp

    if results['timeseries']:
        elaborazione.generate_ts(results['arealstat'], str(results['dekadal'][0]), str(results['dekadal'][1]), results['timeseries'])

    L1_AGBP_summed, ETaColl1, ETaColl2, ETaColl3, WPbm = elaborazione.image_processing(abpm, aet)

    if results['arealstat']:

        tempo_0 = datetime.datetime.now()
        ritornati = elaborazione.generate_areal_stats(results['arealstat'], WPbm)
        tempo_1 = datetime.datetime.now()
        trascorso = tempo_1-tempo_0
        trascorso_secondi = trascorso.seconds
        messaggio = "Stats for {} in {} between {} and {} \nSTDev {} \nMIN {} \nMAX {} \nMEAN {} \nin {} secs".format(
                                                                results['arealstat'],
                                                                'Water productivity',
                                                                str(results['dekadal'][0]),
                                                                str(results['dekadal'][1]),
                                                                ritornati['std'],
                                                                ritornati['min'],
                                                                ritornati['max'],
                                                                ritornati['mean'],
                                                                trascorso_secondi)
        print messaggio

    if results['map_id']:
        print elaborazione.map_id_getter(WPbm)

    if results['chart']:
        elaborazione.image_visualization('c', L1_AGBP_summed, ETaColl3, WPbm)
    elif results['map']:
        elaborazione.image_visualization('m', L1_AGBP_summed, ETaColl3, WPbm)
    else:
        pass

    elaborazione.image_export(results['export'], WPbm)


if __name__ == '__main__':
    results = main()
    run(results)
