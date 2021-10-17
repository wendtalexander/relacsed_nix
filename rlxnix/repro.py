from IPython.terminal.embed import embed
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
    def name(self) -> str:
        """The name of the repro run

        Returns:
            string: the name
        """
        return self._repro_run.name

    @property
    def type(self) -> str:
        """The type of the repro run

        Returns:
            string: the type
        """
        return self._repro_run.type

    @property
    def start_time(self) -> float:
        """The start time of the 

        Returns:
            float: RePro start time
        """
        return self._start_time

    @property
    def duration(self) -> float:
        """The duration of the repro run in seconds.

        Returns:
            float: the duration in seconds.
        """
        return self._duration

    @property
    def repro_tag(self) -> nixio.Tag:
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._repro_run

    @property
    def references(self) -> list:
        """The list of referenced event and data traces

        Returns:
            List: index, name and type of the references
        """
        refs = []
        for i, r in enumerate(self._repro_run.references):
            refs.append(f"{i}: {r.name} -- {r.type}")
        return refs

    @property
    def features(self) -> list:
        """List of features associated with this repro run.

        Returns:
            List: name and type of t[description]
        """
        features = []
        for i, feats in enumerate(self._repro_run.features):
            features.append(f"{i}: {feats.data.name} -- {feats.data.type}")
        return features

    def __str__(self) -> str:
        info = "Repro: {n:s} \t type: {t:s}\n\tstart time: {st:.2f}s\tduration: {et:.2f}s"
        return info.format(n=self.name, t=self.type, st=self.start_time, et=self.duration)

    def __repr__(self) -> str:
        return super().__repr__()