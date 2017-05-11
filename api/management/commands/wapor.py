from django.core.management.base import BaseCommand
from wapor_algorithms import wpMain
import argparse
import datetime
# ...


class Command(BaseCommand):
    # help = 'Run the wapor algorithms with parameters'

    def valid_date(s):
        try:
            return datetime.datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            msg = "Not a valid date: '{0}'.".format(s)
            raise argparse.ArgumentTypeError(msg)

    def add_arguments(self, parser):
        # retrieve arguments
        # parser = argparse.ArgumentParser(prog='manage.py wapor')
        # import ipdb; ipdb.set_trace()
        # wpMain.main()
        # parser = argparse.ArgumentParser(description='Water Productivity using Google Earth Engine')
        groupTimePeriod = parser.add_mutually_exclusive_group()
        groupTimePeriod.add_argument("-a",
                                     "--annual",
                                     metavar='Year',
                                     type=int,
                                     help="Calculate Water Productivity Annually"
                                          " - Year must be provided",
                                     default=0)
        # import ipdb; ipdb.set_trace()
        groupTimePeriod.add_argument("-d",
                                     "--dekadal",
                                     metavar="Start End Dates",
                                     help="Calculate Water Productivity for dekads"
                                          " - Starting and ending date must"
                                          " be provided with the following "
                                          "format YYYY-MM-DD",
                                     nargs=2,
                                     )# type=self.valid_date)

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
        # for argument in arguments:
        #     parser.add_arguments(argument)

    def handle(self, *args, **options):
        # run the script
        # import ipdb; ipdb.set_trace()
        wpMain.run(options)
