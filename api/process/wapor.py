from django.core.management import call_command
from StringIO import StringIO
# from jsonpickle import encode, decode
import sys
# import json
import ast


class Wapor:
    """docstring for Wapor"""
    # def __init__(self, *args):
    #     super(Wapor, self).__init__()
    #     for arg in args:
    #         self.arg = arg
    def run(self):

        # from IPython import embed; embed();
        old_stdout = sys.stdout
        # This variable will store everything that is sent to the
        # standard output
        cmd = StringIO()
        sys.stdout = cmd

        # Here we can call anything we like, like external modules,
        # and everything that they will send to standard output will be
        # stored on "cmd"
        # import ipdb; ipdb.set_trace()
        call_command('wapor',
                     '2015-1-1',
                     '2015-1-30',
                     map_id=True,
                     aggregation='wp_gb')

        # Redirect again the std output to screen
        sys.stdout = old_stdout
        result_string = cmd.getvalue().split("RESULT=", 1)[1]
        result = ast.literal_eval(result_string)
        # result = json.dumps(result_string)

        return result
