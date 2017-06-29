"""Summary
"""
from django.core.management.base import CommandParser
import argparse
import argparse2json
import json


# class MyArgParser(argparse.ArgumentParser):
#   def __init__(self, *args, **kwargs):
#     self._option_lists = {}
#     super(MyArgParser, self).__init__(*args, **kwargs)

#   def parse_args(self, *args, **kw):
#     self._action_groups.append(OptionListGroup(self._option_lists.values()))
#     return super(MyArgParser, self).parse_args(*args, **kw)

#   def add_option_list(self, name, lst):
#     if name in map(itemgetter(0), self._option_lists.values()):
#       raise ValueError, "Name already existing"
#     self._option_lists[id(lst)] = (name, lst)

#   def add_argument(self, *args, **kw):
#     name_list = self._option_lists.get(id(kw.get('choices')))
#     if name_list:
#       kw['metavar'] = name_list[0]
#     return super(MyArgParser, self).add_argument(*args, **kw)


class Arguments(CommandParser):
    """docstring for Arguments
    """
    def __init__(self, **kwargs):
        """Summary

        Args:
            **kwargs: Description
        """
        super(Arguments, self).__init__(self, **kwargs)


def add_option_group(parser, lst): #TODO adapt to add_option logic
    """Summary

    Args:
        parser (TYPE): Description
        lst (TYPE): Description

    Returns:
        TYPE: Description
    """
    opts = []
    for element in lst:
        opts.append(element['commands'])
        arg = ', '.join('%s' % y for y in element['commands'])
        # print 'arg=', arg
        try:
            element.pop("commands", None)
            kw = ', '.join('%s=%r' % x for x in element.iteritems())
            # print 'kw=', kw
        except KeyError:
            pass
        group = parser.add_mutually_exclusive_group()
        group.add_argument(arg + ', ' + kw)
        # print 'group=', group
    # print 'opts is ', opts
    # print 'group=', group
    return parser


def add_option(parser, opts):
    """Summary

    Args:
        parser (TYPE): Description
        opts (TYPE): Description

    Returns:
        TYPE: Description
    """
    # print 'opt=', opts
    if is_optional(opts):
        # logic for optional item
        arg = ', '.join('%s' % y for y in opts['commands'])
        # print 'arg=', arg
        # from IPython import embed; embed();
        # import ipdb; ipdb.set_trace()
        try:
            opts.pop("commands", None)
            if not opts.get('nargs'):
                opts['nargs'] = '*'
            if not opts.get('choices'):
                opts.pop('choices', None)
            if 'display_name' in opts:
                if not ('dest' in opts):
                    opts['dest'] = opts.get('display_name')
            opts.pop("display_name", None)
            kw = opts
            # print 'kw=', kw
        except KeyError:
            pass
        parser.add_argument(arg, **kw)
    else:
        # logic for positional item
        opts.pop('commands')
        pos = opts.get('display_name')
        # print 'pos=', pos

        try:
            # if 'display_name' in opts:
            #     if not ('dest' in opts):
            #         opts['dest'] = opts.get('display_name')
            if not opts.get('nargs'):
                opts['nargs'] = None
            if not opts.get('choices'):
                opts['choices'] = None
            # opts = safe_option(opts)
            opts.pop("display_name", None)
            kw = opts
            # print 'kw=', kw
        except KeyError:
            pass
        parser.add_argument(pos, **kw)

    return parser


def safe_option(opt):
    """Summary

    Args:
        opt (TYPE): Description

    Returns:
        TYPE: Description
    """
    for key in opt.iteritems:
        if not opt.get(key):
            opt[key] = None
    return opt


def is_optional(opt):
    '''option not positional or possessing the `required` flag

    Args:
        opt (TYPE): Description

    Returns:
        TYPE: Description
    '''
    return (not is_empty(opt['commands'])) and (is_flag(opt.get('commands')) or opt['required'])


def is_flag(opt):
    """Summary

    Args:
        opt (TYPE): Description

    Returns:
        TYPE: Description
    """
    for flag in opt:
        if flag.startswith('-'):
            return True
            break
        else:
            return False


def is_empty(any):
    """Summary

    Args:
        any (TYPE): Description

    Returns:
        TYPE: Description
    """
    if any:
        # print('Structure is not empty.')
        return False
    else:
        # print('Structure is empty.')
        return True


def json2argparse(parser, options, **kwargs):
    """Summary

    Args:
        parser (TYPE): Description
        options (TYPE): Description
        **kwargs: Description

    Returns:
        TYPE: Description
    """
    # http://stackoverflow.com/questions/33893970/python-how-can-i-ingest-arguments-from-json-file
    # http://stackoverflow.com/questions/9702414/extend-argparse-to-write-set-names-in-the-help-text-for-optional-argument-choice
    # https://bitbucket.org/ellethee/argparseinator/overview
    # https://github.com/gpocentek/data2args/blob/master/docs/source/getting_started.rst
    # https://github.com/sgarcez/arseparse
    # https://bitbucket.org/ruamel/std.argparse/
    for option in options:
        # import ipdb; ipdb.set_trace()
        # print 'option=', json.dumps(option['option'])
        if isinstance(option['option'], list):
            # print 'list is ', option['option']
            add_option_group(parser, option['option'])

        if isinstance(option['option'], dict):
            # print 'dict is ', option['option']
            add_option(parser, option['option'])
        else:
            pass

    return parser


def read_options(fnc, **kwargs):
    """Parse an argparse parser and return an array

    Args:
        fnc (TYPE): Description
        **kwargs: Description

    Returns:
        TYPE: Description
    """
    if isinstance(fnc.__call__(), argparse.ArgumentParser):
        # print argparse2json.convert(fnc.__call__())['widgets']['primary']['contents']
        datas = argparse2json.convert(fnc.__call__())['widgets']['primary']['contents']
        options = []
        for data in datas:
            opts_list = {}
            # print json.dumps(data['data'])
            opts_list['option'] = data['data']
            options.append(opts_list)
        # print 'options', json.dumps(options)
        return options


def test(parser):
    """Summary

    Args:
        parser (TYPE): Description
    """
    group_output = parser.add_mutually_exclusive_group()
    group_output.add_argument("-c", "--chart",
                              help="x",
                              action="store_true")

    group_output.add_argument("-f", "--fap",
                              help="x",
                              action="store_true")

    groupTimePeriod = parser.add_mutually_exclusive_group()
    groupTimePeriod.add_argument("-k",
                                 "--kannual",
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
                                 )
