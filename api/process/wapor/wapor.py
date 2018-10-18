"""Generic class for Wapor processing
"""
from api.process.base import Base


NAMESPACE = "wapor"
SYNC = "SYNC"
ASYNC = "ASYNC"


class Wapor(Base):
    """Execute Wapor processes

    Parameters
    ----------
        namespace: string
            A namespace for the process
        mode: string
            A mode for the process that can be SYNC or ASYNC
    """

    def __init__(self, mode=SYNC):
        Base.__init__(self)
        self.namespace = NAMESPACE
        self.mode = mode

    # properties
    @property
    def mode(self):
        """Retrieves mode from instance"""
        return self.__mode

    @mode.setter
    def mode(self, value):
        """Sets new value for attribute mode

        Parameters
        ----------
        value : string
            Assign new mode to instance

        """
        self.__mode = value

    def run(self, algorithm):
        """Execute the algorithm.

        Parameters
        ----------
        algorithm : string
            A determined algorithm in the namespace

        Returns
        -------
        dict
            An object that contains the primary keys 'maps',
            'stats' and eventually 'errors' for any failure during
            the execution.
        """
        # dynamic import of class https://www.bnmetrics.com/blog/dynamic-import-in-python3
        # from wapor.algorithms.uda.wp import WP

        alg = ALG(**kwargs)
        if self.mode == SYNC:
            output = wp.execute()
        else:
            pass

        result = {
            "maps": output["outputs"]["maps"],
            "stats": output["outputs"]["stats"],
            "errors": output["errors"]
        }

        return result
