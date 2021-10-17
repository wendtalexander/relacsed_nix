import nixio

class RePro(object):
    """This class represents the data of a RePro run. It offers access to the data and metadata.
    """

    def __init__(self, repro_run: nixio.Tag, relacs_nix_version=1.1):
        """Create a RePro instance that represent one run of a relacs RePro.

        Args:
            repro_run (nixio.Tag): the nix - tag that belong to the repro run 
            relacs_nix_version (float, optional): The mapping version number. Defaults to 1.1.
        """
        super().__init__()
        self._repro_run = repro_run
        self._relacs_nix_version = relacs_nix_version
        self._start_time = repro_run.position[0]
        self._duration = repro_run.extent[0]

    @property
    def name(self):
        """The name of the repro run

        Returns:
            string: the name
        """
        return self.repro_run.name

    @property
    def type(self):
        """The type of the repro run

        Returns:
            string: the type
        """
        return self.repro_run.type

    @property
    def start_time(self):
        """The start time of the 

        Returns:
            [type]: [description]
        """
        return self._start_time

    @property
    def duration(self):
        return self._duration

    @property
    def repro_tag(self):
        return self._repro_run