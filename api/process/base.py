"""Base class for a process
"""


class Base:
    """Initialize Base class

    Parameters
    ----------
    name: string
        name of the process, empty by default
    inputs: dict
        inputs of the process, empty by default
    options: dict
        options of the process, empty by default
    outputs: dict
        outputs of the process, empty by default
    state: string
        state of the process, empty by default
    """

    def __init__(self, name="", inputs={}, options={}, outputs={}, state=""):
        self.name = name
        self.inputs = inputs
        self.options = options
        self.outputs = outputs
        self.state = state

    # properties
    @property
    def name(self):
        """Retrieves name from instance"""
        return self.__name

    @property
    def inputs(self):
        """Retrieves inputs from instance"""
        return self.__inputs

    @property
    def options(self):
        """Retrieves options from instance"""
        return self.__options

    @property
    def outputs(self):
        """Retrieves outputs from instance"""
        return self.__outputs

    @property
    def state(self):
        """Retrieves state from instance"""
        return self.__state

    # setters
    @name.setter
    def name(self, value):
        """Sets new value for attribute name

        Parameters
        ----------
        value : string
            Assign new name to instance

        """
        self.__name = value

    @inputs.setter
    def inputs(self, value):
        """Sets new value for attribute inputs

        Parameters
        ----------
        value : dict
            Assign new inputs to instance

        """
        self.__inputs = value

    @options.setter
    def options(self, value):
        """Sets new value for attribute options

        Parameters
        ----------
        value : dict
            Assign new options to instance

        """
        self.__options = value

    @outputs.setter
    def outputs(self, value):
        """Sets new value for attribute outputs

        Parameters
        ----------
        value : dict
            Assign new outputs to instance

        """
        self.__outputs = value

    @state.setter
    def state(self, value):
        """Sets new value for attribute state

        Parameters
        ----------
        value : string
            Assign new state to instance

        """
        self.__state = value

    def run(self, algorithm):
        """Execute the algorithm.

        Parameters
        ----------
        algorithm : string
            Execute a determined algorithm in the name space
        """
        pass
