import nixio

from .trace_container import TraceContainer
from .stimulus import Stimulus
from .util import nix_metadata_to_dict


class ReProRun(TraceContainer):
    """This class represents the data of a RePro run. It offers access to the data and metadata.
    """

    def __init__(self, repro_run: nixio.Tag, relacs_nix_version=1.1):
        """Create a RePro instance that represent one run of a relacs RePro.

        Args:
            repro_run (nixio.Tag): the nix - tag that belong to the repro run 
            relacs_nix_version (float, optional): The mapping version number. Defaults to 1.1.
        """
        super().__init__(repro_run, relacs_nix_version=relacs_nix_version)
        self._stimuli = []
    
    @property
    def metadata(self):
        m = nix_metadata_to_dict(self._repro_run.metadata)
        return m

    def add_stimulus(self, stimulus:Stimulus):
        self._stimuli.append(stimulus)

    @property
    def stimuli(self):
        return self._stimuli

    def __str__(self) -> str:
        info = "Repro: {n:s} \t type: {t:s}\n\tstart time: {st:.2f}s\tduration: {et:.2f}s"
        return info.format(n=self.name, t=self.type, st=self.start_time, et=self.duration)

    def __repr__(self) -> str:
        return super().__repr__()