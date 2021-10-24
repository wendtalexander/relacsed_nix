from inspect import trace
import nixio
import numpy as np
from enum import Enum
import logging

from .mappings import DataType, type_map


class TimeReference(Enum):
    """Enumeration to control the time axis returned by the trace_data function.
    Options are:
        * ReproStart: the time axis will start at the start time of the ReproRun, respectively the stimulus start
        * Zero: the time axis will start at zero, by subtracting the start time
    """
    ReproStart = 0
    Zero = 1


class TraceContainer(object):
    """Superclass for classes that are based on nix Tags/MultiTags. Provides some general properties and functions for accessing the data and some basic properties.
    """
    def __init__(self, tag_or_mtag, index=None, relacs_nix_version=1.1) -> None:
        """Constructor of TraceContainer class.

        Parameters
        ----------
        tag_or_mtag: nixio.Tag or nixio.MultiTag
            The tags that reference the recorded data.
        index: int
            In the case that a MultiTag is passed and the container represent a stimulus output, an index must be provided. Defaults to None.
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
        self._trace_names = None
        self._trace_map = {}
        self._max_times = {}

        if isinstance(self._tag, nixio.MultiTag):
            self._start_time = self._tag.positions[self._index, 0][0]
            self._duration = self._tag.extents[self._index, 0][0] if self._tag.extents else 0.0
        else:
            self._start_time = self._tag.position[0]
            self._duration = self._tag.extent[0] if self._tag.extent else 0.0

        self._scan_traces()

    def _scan_traces(self):
        # FIXME it is actually stupid to do it for every trace container... extract class of its own, create ind dataset and pass it to all reproRuns and stimuli.
        continuous_data_type = type_map[self._mapping_version][DataType.continuous]
        self._trace_names = []
        for i, r in enumerate(self._tag.references):
            self._trace_names.append((i, r.name, r.type))
            self._trace_map[r.name] = r
            if continuous_data_type in r.type:
                self._max_times[r.name] = r.shape[0] * r.dimensions[0].sampling_interval

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
        refs = []
        for i, r in enumerate(self._tag.references):
            refs.append((i, r.name, r.type))
        return refs

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

    def trace_data(self, name_or_index, reference=TimeReference.Zero):
        """Get the data that was recorded while this repro was run.

        Paramters
        ---------
        name_or_index: (str or int)
            name or index of the referenced data trace e.g. "V-1" for the recorded voltage
        reference: TimeReference
            Controls the time reference of the time axis and event times. If TimeReference.ReproStart is given all times will start after the Repro/Stimulus start. Defaults to TimeReference.Zero, i.e. all times will start at zero, the RePro/stimulus start time will be subtracted from event times and time axis.

        Returns
        -------
        data: np.ndarray
            The recorded continuos or event data 
        time: np.ndarray
            The respective time vector for continuous traces, None for event traces
        """
        logging.debug(f"reading trace data from {name_or_index}, with time reference {reference}")
        ref = self._tag.references[name_or_index]
        time = None
        continuous_data_type = type_map[self._mapping_version][DataType.continuous]
        logging.debug(f"get data slice from {self.start_time} to {self.start_time + self.duration}")
        data = ref.get_slice([self.start_time], [self.duration], nixio.DataSliceMode.Data)[:]
        start_position = self.start_time if reference is TimeReference.ReproStart else 0.0

        if continuous_data_type in ref.type:  
            time = np.array(ref.dimensions[0].axis(len(data), start_position=start_position))
        else:  # event data
            data -= self.start_time
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