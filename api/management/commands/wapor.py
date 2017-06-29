"""Summary
"""
from django.core.management.base import BaseCommand
from wapor_algorithms import wpMain
from util.arguments import (Arguments,
                            read_options,
                            json2argparse)
import argparse
# ...


class Command(BaseCommand):
    """Summary
    """
    # help = 'Run the wapor algorithms with parameters'
    # See http://www.itkeyword.com/doc/6843479563087088172/is-it-possible-to-create-subparsers-in-a-django-management-command
    # for subparser
    def __init__(self, *args, **kwargs):
        """Summary

        Args:
            *args: Description
            **kwargs: Description
        """
        super(Command, self).__init__(*args, **kwargs)


    def add_arguments(self, parser):
        """Summary

        Args:
            parser (TYPE): Description
        """
        # import ipdb; ipdb.set_trace()
        myoptions = read_options(wpMain.setup)

        # arguments = vars(wpMain.setup())
        # print '-----------------------------'
        json2argparse(parser, myoptions)

        # parser.add_argument("timeframe",
        #                     nargs="*",
        #                     help="Calculate Water Productivity Annually for the chosen period"
        #                     )

        # parser.add_argument('-x', '--export', choices=['u', 'd', 't'],
        #                     help="Choose export to url(-u), drive (-d) or asset (-t)")

        # parser.add_argument('-i', '--map_id',
        #                     help="Generate map id for generating tiles",
        #                     action="store_true")

        # parser.add_argument('-s', '--arealstat',
        #                     help="Zonal statistics form a WaterProductivity generated in GEE for the chosen country")

        # parser.add_argument('-o', '--output',
        #                     choices=['csv', 'json'],
        #                     help="Choose format fo the annual statistics csv(-o 'csv') or json (-o 'json')")

        # parser.add_argument("-a",
        #                     "--aggregation",
        #                     choices=['agbp', 'aet', 't_frac', 'wp_gb', 'wp_nb'],
        #                     help="Aggregate dekadal data at annual level"
        #                     )

        # parser.add_argument("-m",
        #                     "--map",
        #                     choices=['agbp', 'aet', 't_frac', 'wp_gb', 'wp_nb'],
        #                     help="Show calculated output overlaid on Google Map"
        #                     )

    def handle(self, *args, **options):
        """Summary

        Args:
            *args: Description
            **options: Description
        """
        # run the script
        # import ipdb; ipdb.set_trace()
        # print 'final options:', options
        arguments = argparse.Namespace(**options)
        # print 'final arguments:', arguments
        wpMain.run(arguments)
