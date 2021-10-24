from inspect import trace
import nixio
import numpy as np
from enum import Enum
import logging

from .mappings import DataType, type_map


class TimeReference(Enum):
    """Enumeration to control the time axis returned by the trace_data function.
    Options are:
        * Absolute: the time axis will be in absolute time
        * Zero: the time axis will is zero at segment start
    """
    Absolute = 0
    Zero = 1


class TraceContainer(object):
    """Superclass for classes that are based on nix Tags/MultiTags. Provides some general properties and functions for accessing the data and some basic properties.
    """
    def __init__(self, tag_or_mtag, traces, index=None, relacs_nix_version=1.1) -> None:
        """Constructor of TraceContainer class.

        Parameters
        ----------
        tag_or_mtag: nixio.Tag or nixio.MultiTag
            The tags that reference the recorded data.
        traces: map of rlxnix.DataTrace
            Map of DataTrace infos.
        index: int, optional
            The index in the Stimulus tag that relates to the stimulus.
        relace_nix_version: float
            The relacs to nix mapping version, Defaults to 1.1
        """
        super().__init__()
        if isinstance(tag_or_mtag, nixio.MultiTag) and index is None:
            logging.error("Index must not be None, if a multiTag is passed!")
            raise ValueError("Index must not be None, if a multiTag is passed!")

        self._tag = tag_or_mtag
        self._mapping_version = relacs_nix_version
        self._index = index
        self._features = None
        self._trace_map = traces

        if isinstance(self._tag, nixio.MultiTag):
            self._start_time = self._tag.positions[self._index, 0][0]
            self._duration = self._tag.extents[self._index, 0][0] if self._tag.extents else 0.0
        else:
            self._start_time = self._tag.position[0]
            self._duration = self._tag.extent[0] if self._tag.extent else 0.0

    @property
    def name(self) -> str:
        """The name of the data segment

        Returns
        -------
        string
            the name
        """
        return self._tag.name

    @property
    def type(self) -> str:
        """The type of the data segment

        Returns
        -------
        string 
            the type
        """
        return self._tag.type

    @property
    def start_time(self) -> float:
        """The start time of the repro run or the stimulus output. The stimulus time is given in "data time", that is the amount of time in which data was dumped to file.

        Returns
        -------
        float 
            RePro start time
        """
        return self._start_time

    @property
    def duration(self) -> float:
        """The duration of the repro run in seconds.

        Returns
        -------
        float
            the duration in seconds.
        """
        return self._duration

    @property
    def stop_time(self):
        """Stop time pf the stimulus segment.

        Returns
        -------
        float
            The stimulus stop time.

        """
        return self.start_time + self.duration

    @property
    def repro_tag(self):
        """Returns the underlying tag

        Returns
        -------
        nixio Tag or MultiTag
            the tag
        """
        return self._tag

    @property
    def traces(self) -> list:
        """The list of referenced event and data traces

        Returns
        -------
            List: index, name and type of the references
        """
        
        return list(self._trace_map.keys())

    @property
    def features(self) -> list:
        """List of features associated with this repro run.

        Returns
        -------
        list of tuples
            index, name and type of t
        """
        if self._features is None:
            self._features = []
            for i, feats in enumerate(self._tag.features):
                self._features.append((i, feats.data.name, feats.data.type))
        return self._features

    def _trace_data(self, name, before=0.0, after=0.0, reference=TimeReference.Zero):
        """Get the data that was recorded while this repro was run, the stimulus was put out.

        Paramters
        ---------
        name: str
            name of the referenced data trace e.g. "V-1" for the recorded voltage.
        before: float
            Time before segment start that should be read. Defaults to 0.0.
        after: float
            Additional time after segment stop. Defaults t0 0.0
        reference: TimeReference
            Controls the time reference of the time axis and event times. If TimeReference.Absolute is given all times will be in absolute data time. Defaults to TimeReference.Zero, i.e. segment start will be set to zero.

        Returns
        -------
        data: np.ndarray
            The recorded continuos or event data 
        time: np.ndarray
            The respective time vector for continuous traces, None for event traces
        """
        if self.stop_time < self.start_time:
            logging.warning(f"TraceContainer._trace_data: reading trace data from {name}, slice is invalid! start_time: {self.start_time} stop_time: {self.stop_time}. Interrupted stimulus?")
            return None, None

        logging.debug(f"TraceContainer._trace_data: reading trace data from {name}, with time reference {reference}")
        if name not in self._tag.references or name not in self._trace_map.keys():
            raise ValueError(f"Could not find {name} in the list of references.")
        ref = self._trace_map[name]
        
        segment_stop_time = self.start_time + self.duration + after
        
        if ref.trace_type == DataType.continuous:
            if segment_stop_time > ref.maximum_time:
                after = ref.maximum_time - self.stop_time
                logging.warning(f"traceContainer._trace_data: segment stop time ({np.round(segment_stop_time, 5)}) is too large, beyond maximum time in trace {ref.name} ({ref.maximum_time})! reduced after to {np.round(after, 5)}!")
                segment_stop_time = self.start_time + self.duration + after

        logging.debug(f"TraceContainer._trace_data: get data slice from {np.round(self.start_time - before, 5)} to {np.round(segment_stop_time, 5)}")
        
        data = ref.data_array.get_slice([self.start_time - before], [self.duration + after + before], nixio.DataSliceMode.Data)[:]
        time = None

        if ref.trace_type == DataType.continuous:  
            time = np.array(ref.data_array.dimensions[0].axis(len(data)))
            if reference == TimeReference.Absolute:
                time += (self.start_time - before)
            else:
                time -= before
        else:  # event data
            data -=  0.0 if reference is TimeReference.Absolute else self.start_time
        return data, time

    def feature_data(self, name_or_index):
        """Get the feature data that is related to this ReproRun or stimulus

        Parameters
        ----------
        name_or_index : str or int
            The name or the index of the feature (consult the features property to see which features are stored)

        Returns
        -------
        numpy.ndarray
            The feature data.

        Raises
        ------
        ValueError
            If this container is a Stimulus and there is no position index stored, a ValueError is raised, should never happen.
        """
        if isinstance(self._tag, nixio.MultiTag) and self._index is not None:
            logging.debug(f"reading feature data from {name_or_index} with index {self._index}")
            feat_data = self._tag.feature_data(self._index, name_or_index)
        elif isinstance(self._tag, nixio.Tag):    
            logging.debug(f"reading feature data from {name_or_index}")
            feat_data = self._tag.feature_data(name_or_index)
        else:
            raise ValueError(f"TraceContainer, feature_data: something went wrong, no Index? Tag: {self._tag}, Index:{self._index}")
        return feat_data[:]