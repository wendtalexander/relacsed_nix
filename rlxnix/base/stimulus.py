import nixio
import logging
import numpy as np

from .trace_container import TraceContainer, TimeReference
from ..utils.util import nix_metadata_to_dict, metadata_to_json
from ..utils.buffers import MetadataBuffer
from ..utils.data_loader import DataLink, SegmentType


class Stimulus(TraceContainer):
    """Class that represents a single stimulus segment. It provides access to the stimulus metadata and the data traces.
    """
    def __init__(self, stimulus_multi_tag: nixio.MultiTag, index: int, traces, 
                 next_stimulus_start=None, relacs_nix_version=1.1) -> None:
        """Create an instance of the Stimulus class.

        Parameters
        ----------
        stimulus_multi_tag : nixio.MultiTag
            The MultiTag that contains the data. 
        index : int
            The index of the stimulation. (A MultiTag tag several segments in which the same, or similar stimulus was presented.)
        traces: dict of rlxnix.DataTrace
            Dict of trace infos.
        next_stimulus_start: float
            The start time of the next stimulus, defaults to None.
        relacs_nix_version : float, optional
            relacs data to nix mapping version, by default 1.1
        """
        super().__init__(stimulus_multi_tag, index, traces, relacs_nix_version=relacs_nix_version)
        self._multi_tag = stimulus_multi_tag
        self._metadata_buffer = MetadataBuffer()
        self._metadata = None
        self._absolute_starttime = None
        self._delay = None
        self._next_stimulus_start = next_stimulus_start
        logging.debug(self.__str__())

    @property
    def repro_tag_id(self):
        """Returns the id of the ReproRun tag, to which this stimulus output belongs.

        Returns
        -------
        str
            the Repro Tag id.
        """
        feat_name = "_".join((self.name, "repro_tag_id"))
        if feat_name in self._tag.features:
            repro_id = self.feature_data(feat_name).ravel()[0]
        return repro_id

    @property
    def metadata(self):
        """Returns the metadata for this stimulus. The settings herein complete and supersede the ones of the RePro. For a complete view use the ReProRun.stimulus_metadata property.

        Returns:
        --------
            metadata: dict
                The metadata dictionary
        """
        def find_subdict(mdata, key):
            if key in mdata.keys():
                return mdata[key]
            for k in mdata.keys():
                subdict = mdata[k]
                if isinstance(subdict, dict):
                    if key in subdict:
                        return subdict[key]
                    found = find_subdict(subdict, key)
                    if found is not None:
                        return found
                else:
                    continue
            return None

        def update_metadata(mdata, key, value, unit):
            if "." not in key:
                mdata[key] = (value, unit)
            else:
                parts = key.split(".")
                if parts[0] in mdata.keys():
                    update_metadata(mdata[parts[0]], ".".join(parts[1:]), value, unit)
                else:
                    mdata = find_subdict(mdata, parts[0])
                    if mdata is not None:
                        update_metadata(mdata, ".".join(parts[1:]), value, unit)
                    else:
                        logging.error(f"Could not find subdict for key {parts[0]}! Skipping")

        if self._metadata is None:
            if self._metadata_buffer.has(self.id):
                metadata = self._metadata_buffer.get(self.id)
            else:
                metadata = nix_metadata_to_dict(self._tag.metadata)
                self._metadata_buffer.put(self.id, metadata.copy())

            for index, name, type in self.features:
                if "mutable" in type:
                    suffix = name.split(self.name + "_")[-1]
                    try:
                        feature_data = self.feature_data(name)
                    except:
                        logging.error(f"Could not read feature data for {name}! Skipped!")
                        continue
                    feature_unit = self._tag.features[index].data.unit
                    update_metadata(metadata[self.name], suffix, feature_data.ravel().tolist(), feature_unit)
            self._metadata = metadata
        return self._metadata

    @property
    def absolute_start_time(self) -> float:
        """The absolute time at which the stimulus started relative to the onset of the recording. Since relacs does not necessarily store data during the whole recording period, the absolute time will deviate from the stimulus start time.

        Returns
        -------
        float
            The absolute start time of the stimulus
        """
        if self._absolute_starttime is None:
            feat = self._find_feature("_abs_time")
            if feat is not None:
                self._absolute_starttime = float(self.feature_data(feat))
        return self._absolute_starttime

    @property
    def delay(self) -> float:
        """The delay between beginning of data recording and the actual stimulus output. This is the maximum time one can read data from file before the stimulus onset. Reading data from before -delay relative to stimulus onset may give invalid data.

        Returns
        -------
        float
            The delay between acquisition start and stimulus output.
        """ 
        if self._delay is None:
            feat = self._find_feature("_delay")
            if feat is not None:
                self._delay = float(self.feature_data(feat))
        return self._delay

    @property
    def next_stimulus_start(self) -> float:
        """Returns the start time of the next stimulus output, if any.

        Returns
        -------
        float
            The next stimulus start time (in data time), or None, if no stimulus is following.
        """
        return self._next_stimulus_start

    def _find_feature(self, feature_suffix) -> str:
        """Find a feature with a certain suffix in the list of features.

        Parameters
        ----------
        feature_suffix : str
            The features suffix including the underscore, e.g. "_delay"

        Returns
        -------
        str
            the full name of the feature if it exists, otherwise None
        """
        feat = None
        for _, f, _ in self.features:
            if self.name + feature_suffix in f:
                feat = f
                break
        return feat

    def trace_data(self, name, before=0.0, after=0.0, reference=TimeReference.Zero):
        """Get the data that was recorded while this stimulus was put out. With before and after, the timespan can be extended. before must not be larger than the delay, stimulus stop + after must not reach into the next stimulus start. They will be automatically adjusted.

        Paramters
        ---------
        name: str
            name of the referenced data trace e.g. "V-1" for the recorded voltage
        before: float
            Time before segment start that should be read. Defaults to 0.0.
        after: float
            Additional time after segment stop. Defaults to 0.0.
        reference: TimeReference
            Controls the time reference of the time axis and event times. If TimeReference.ReproStart is given all times will start after the Repro/Stimulus start. Defaults to TimeReference.Zero, i.e. all times will start at zero, the RePro/stimulus start time will be subtracted from event times and time axis.

        Returns
        -------
        data: np.ndarray
            The recorded continuos or event data 
        time: np.ndarray
            The respective time vector for continuous traces, None for event traces
        """
        if not isinstance(before, float) or not isinstance(after, float):
            logging.error(f"Type of args before and after must be float, got {type(before)} and {type(after)}!")
            return None, None

        if (before > 0.0) and (before > self.delay):
            logging.warning(f"stimulus.trace_data before {before} is larger than delay {self.delay}, before is set to delay!")
            before = self.delay
        if self.next_stimulus_start is None:
            logging.warning(f"stimulus.trace_data after {after} is too large! There is no next stimulus, after is set to zero!")
            after = 0.0
            max_after = 0.0
        else:
            max_after = self.next_stimulus_start - self.stop_time
        if after > 0.0 and after > max_after:
            logging.warning(f"stimulus.trace_data after {np.round(after, 5)} is too large! after is set to next stimulus time - stimulus stop time {np.round(max_after, 5)}!")
            after = max_after

        return self._trace_data(name, before, after, reference)

    def data_link(self):
        """Returns the DataLink object representing this stimulus presentation.

        Returns
        -------
        rlxnix.DataLink
            The DataLink object.
        """
        if self.start_time >= self.stop_time:
            logging.warning(f"Creating DataLink object for stimulus {self.name} fails because stimulus start time {self.start_time} is >= stimulus stop time {self.stop_time}!")
            return None
        dataset = self._tag._parent.name + ".nix"
        block_id = self._tag._parent.id
        tag_id = self.id
        type = SegmentType.StimulusSegment
        mdata = metadata_to_json(self.metadata)
        before = self.delay
        after = 0.0 if self.next_stimulus_start is None else self.next_stimulus_start - self.stop_time 
        dl = DataLink(dataset, block_id, tag_id, type, self.start_time,
                      self.stop_time, index=self._index, 
                      max_before=before, max_after=after, metadata=mdata,
                      mapping_version=self._mapping_version)
        return dl

    def __str__(self) -> str:
        name = self._multi_tag.name
        tag_type = self._multi_tag.type
        info = "Stimulus: {n:s} \t type: {t:s}\n\tstart time: {st:.2f}s, duration: {dur:.2f}s"
        return info.format(n=name, t=tag_type, st=self.start_time, dur=self.duration)

    def __repr__(self) -> str:
        repr = "Stimulus object for stimulus output from {start:.4f} to {stop:.4f}s of MultiTag {id} at {pos}"
        return repr.format(start=self.start_time, stop=self.stop_time, id=self.repro_tag_id, pos=hex(id(self)))