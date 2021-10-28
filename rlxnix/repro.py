import nixio

from .trace_container import TraceContainer, TimeReference
from .stimulus import Stimulus
from .util import nix_metadata_to_dict
from .data_trace import DataType


class ReProRun(TraceContainer):
    """This class represents the data of a RePro run. It offers access to the data and metadata.
    """

    def __init__(self, repro_run: nixio.Tag, traces, relacs_nix_version=1.1):
        """Create a RePro instance that represent one run of a relacs RePro.

        Parameters
        ----------
        repro_run:  nixio.Tag
            the nix - tag that represents the repro run 
        traces: dict of rlxnix.DataTrace
            Dict of trace infos.
        relacs_nix_version:  float
            The mapping version number. Defaults to 1.1.
        """
        super().__init__(repro_run, traces, relacs_nix_version=relacs_nix_version)
        self._stimuli = []
        self._metadata = None

    @property
    def metadata(self):
        """Returns the metadata for this ReProRun. The settings herein are the base settings of the RePro. They may vary for each stimulus. For a complete view use the ReProRun.stimulus_metadata property.

        Returns:
        --------
        dictionary
            The metadata dictionary
        """
        if self._metadata is None:
            self._metadata = nix_metadata_to_dict(self._tag.metadata)
        return self._metadata

    def add_stimulus(self, stimulus:Stimulus):
        """INTERNAL USE ONLY! Adds a stimulus to the list of stimuli run in the context of this RePro run.

        Parameters
        ----------
            stimulus : rlxnix.Stimulus
                The stimulus that was run.
        """
        self._stimuli.append(stimulus)

    @property
    def stimuli(self):
        """List of stimuli run in the context of this RePro Run.

        Returns:
        --------
            stimulus: rlxnix.Stimulus
                The Stimulus instance that provides access to the data during the stimulus output.
        """
        return self._stimuli

    def trace_data(self, name, reference=TimeReference.Zero):
        """Get the data that was recorded while this repro was run.

        Paramters
        ---------
        name: str
            name of the referenced data trace e.g. "V-1" for the recorded voltage.
        reference: TimeReference
            Controls the time reference of the time axis and event times. If TimeReference.ReproStart is given all times will start after the Repro/Stimulus start. Defaults to TimeReference.Zero, i.e. all times will start at zero, the RePro/stimulus start time will be subtracted from event times and time axis.

        Returns
        -------
        data: np.ndarray
            The recorded continuos or event data 
        time: np.ndarray
            The respective time vector for continuous traces, None for event traces
        """
        return self._trace_data(name, reference=reference)

    def _check_stimulus(self, stimulus_index):
        if stimulus_index >= len(self.stimuli) or stimulus_index < 0:
            raise IndexError(f"Stimulus index {stimulus_index} is out of bounds for number of stimuli {len(self.stimuli)}")

    def _check_trace(self, trace_name, data_type=DataType.Continuous):
        if trace_name not in self._tag.references:
            raise ValueError(f"Trace {trace_name} not found!")
        trace = self._trace_map[trace_name]
        if trace.trace_type != data_type:
            raise ValueError(f"Data type of trace {trace.name} does not match expected data type (expected: {data_type}, found: {trace.trace_type}).")

    def __str__(self) -> str:
        info = "Repro: {n:s} \t type: {t:s}\n\tstart time: {st:.2f}s\tduration: {et:.2f}s"
        return info.format(n=self.name, t=self.type, st=self.start_time, et=self.duration)

    def __repr__(self) -> str:
        return super().__repr__()