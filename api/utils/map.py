from collections import namedtuple


Map = namedtuple('Map', ['name', 'rel', 'url'])


class MapUtil:
    """Utility for creating maps object value

    Returns
    -------
    list
        Array of map dictionaries for the 'maps' key

    """

    def __init__(self, maps=[]):
        self.maps = maps

    @property
    def maps(self):
        return self.__maps

    # setters
    @maps.setter
    def maps(self, value):
        """Sets new value for attribute maps

        Parameters
        ----------
        value: string
            Assign new maps to instance

        """
        self.__maps = value

    def add_map(self, map):
        """Add a Map object as dict

        Parameters
        ----------
        map: Map
            Instance of Map object

        Example
        -------
        >>c = EEUtil('projects/fao-wapor/L1/L1_AETI_D')
        >>generated_map = Map(
            name='AETI', rel='projects/fao-wapor/L1/L1_AETI_D',
            url='https://earthengine.googleapis.com/map/e2831907fc7575274fa08097c6c74580/
            {z}/{x}/{y}.png?token=85e66c7aa8d847c167fa468784fba111')
        >>m = MapUtil()
        >>m.add_map(generated_map)
        >>m.maps
        [OrderedDict([('name', 'AETI'),
            ('rel', 'projects/fao-wapor/L1/L1_AETI_D'),
            ('url',
            'https://earthengine.googleapis.com/map/e2831907fc7575274fa08097c6c74580/
            {z}/{x}/{y}.png?token=85e66c7aa8d847c167fa468784fba111')])]

        """

        if isinstance(map, Map):
            self.__maps = self.maps + [map._asdict()]