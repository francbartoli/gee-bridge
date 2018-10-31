"""Generic class for Wapor processing
"""
from api.process.base import Base
from api.process.alg import ALG
from api.process.wapor.algorithms.udwp import UDWP

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

    def __init__(
        self, wapor_name="", wapor_inputs={}, wapor_options={},
        wapor_outputs={}, wapor_state="", mode=SYNC
    ):
        super().__init__(
            name=wapor_name, inputs=wapor_inputs, options=wapor_options,
            outputs=wapor_outputs, state=wapor_state
        )
        if mode not in (SYNC, ASYNC):
            raise ValueError(
                "{0} is not a valid mode.".format(
                    mode
                )
            )
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
            'stats', 'tasks' and eventually 'errors' for any failure during
            the execution.
        """
        # dynamic import of class
        # https://www.bnmetrics.com/blog/dynamic-import-in-python3
        # from wapor.algorithms.uda.wp import WP
        # TODO: the algorithm has to be choosen dynamically and match the
        # list from the catalog
        # alg = ALG()
        alg = UDWP(filters=self.options)

        if self.mode == SYNC:
            output = alg.execute()
        else:
            pass

        result = {
            "maps": output["outputs"]["maps"],
            "stats": output["outputs"]["stats"],
            "tasks": output["outputs"]["tasks"],
            "errors": output["errors"]
        }

        return result
