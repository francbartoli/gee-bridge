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

        """

        if isinstance(map, Map):
            self.__maps = self.maps + [map._asdict()]