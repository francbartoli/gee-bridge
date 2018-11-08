from collections import namedtuple


Stat = namedtuple('Stat', ['name', 'rel', 'stat'])


class StatUtil:
    """Utility for creating stats object value

    Returns
    -------
    list
        Array of stat dictionaries for the 'stats' key

    """

    def __init__(self, stats=[]):
        self.stats = stats

    @property
    def stats(self):
        return self.__stats

    # setters
    @stats.setter
    def stats(self, value):
        """Sets new value for attribute stats

        Parameters
        ----------
        value: string
            Assign new stats to instance

        """
        self.__stats = value

    def add_stat(self, stat):
        """Add a Stat object as dict

        Parameters
        ----------
        stat: Stat
            Instance of Stat object

        Example
        -------
        >>c = EEUtil('projects/fao-wapor/L1/L1_AETI_D')
        >>generated_stat = Stat(
            name='AETI', rel='projects/fao-wapor/L1/L1_AETI_D',
            stat={"max": 2.2239012915851273, "sum": 192173.8123681499,
            "min": 0, "mean": 0.03866244260812292})
        >>s = StatUtil()
        >>s.add_stat(generated_stat)
        >>s.stats
        [OrderedDict([('name', 'AETI'),
            ('rel', 'projects/fao-wapor/L1/L1_AETI_D'),
            ('stat', {"max": 2.2239012915851273, "sum": 192173.8123681499,
            "min": 0, "mean": 0.03866244260812292})])]

        """

        if isinstance(stat, Stat):
            self.__stats = self.stats + [stat._asdict()]