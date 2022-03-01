import nixio
import logging
from tqdm import tqdm

from .trace_container import TraceContainer, TimeReference
from .stimulus import Stimulus
from ..utils.util import nix_metadata_to_dict, metadata_to_json
from ..utils.data_trace import DataType
from ..utils.data_loader import DataLink, SegmentType


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

    def _get_signal_trace_map(self):
        logging.critical("Repro._get_trace_map must be overwritten!")

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
        """List of stimuli that were presented within the context of this RePro Run.

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

    @property
    def stimulus_data_links(self) -> list:
        """Collection of rlxnix.DataLink objects for each stimulus presented in this ReproRun.

        Returns
        -------
        list of rlxnix.DataLink
            List of DataLink objects
        """
        data_links = []
        for s in tqdm(self.stimuli, disable=not(logging.root.level == logging.INFO)):
            dl = s.data_link()
            if dl is not None:
                data_links.append(dl)
        return data_links

    @property
    def data_link(self) -> DataLink:
        """ Returns a DataLink object to the data recorded in this ReproRun

        Returns
        -------
        rlxnix.DataLink
            The DataLink object
        """
        dataset = self.repro_tag._parent.name + ".nix"
        block_id = self.repro_tag._parent.id
        tag_id = self.repro_tag.id
        type = SegmentType.ReproRun
        mdata = metadata_to_json(self.metadata)

        dl = DataLink(dataset, block_id, tag_id, type, self.start_time,
                      self.stop_time, metadata=mdata,
                      mapping_version=self._mapping_version)
        return dl

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
        repr = "ReproRun object for repro run {name} from {start:.4f} to {stop:.4f}s, Tag {id} at {pos}." 
        return repr.format(name=self.name, start=self.start_time, stop=self.stop_time, id=self.repro_tag.id, pos=hex(id(self)))

    def __getitem__(self, key) -> Stimulus:
        if isinstance(key, int):
            return self._stimuli[key]
        else:
            raise KeyError(f"Key is invalid! {key} is not instance of int.")

