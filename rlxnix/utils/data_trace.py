import logging

from .mappings import DataType, type_map


class DataTrace(object):
    """The DataTrace class represents a recorded data trace. The trace_type property holds whether the trace is an event or a continuously sampled trace. It further keeps the maximum number of samples and the maximum time information. It further provides access to the underlying nixio.DataArray.
    """
    
    def __init__(self, data_array, mapping_version=1.1) -> None:
        super().__init__()
        event_type = type_map[mapping_version][DataType.Event]
        continuous_type = type_map[mapping_version][DataType.Continuous]
        t = data_array.type
        if (event_type not in t) and (continuous_type not in t):
            raise ValueError(f"DataTrace not valid to dataArrray of type {data_array.type}!")
        self._data_array = data_array
        self._name = data_array.name
        self._id = data_array.id
        self._type = data_array.type
        self._trace_type = DataType.Continuous if continuous_type in data_array.type else DataType.Event
        self._shape = data_array.shape
        self._sampling_interval = None
        if self._trace_type == DataType.Event:
            if sum(data_array.shape) > 0:
                self._max_time = data_array[-1]
            else:
                self._max_time = 0.0
        else:
            self._max_time = self._shape[0] * data_array.dimensions[0].sampling_interval
            self._sampling_interval = data_array.dimensions[0].sampling_interval

    @property
    def trace_type(self):
        """The DataType stored in this trace. Either DataType.Continuous for continuously sampled data or DataType.Event for event type data.

        Returns
        -------
        DataType
            The DataType of this trace.
        """
        return self._trace_type

    @property
    def maximum_time(self):
        """The maximum time represetend in this Trace

        Returns
        -------
        float
            The maximum time
        """
        return self._max_time

    @property
    def shape(self):
        """The ashape of the stored data

        Returns
        -------
        tuple
            The DataArray shape.
        """
        return self._shape
    
    @property
    def name(self):
        """The name of this trace.

        Returns
        -------
        str
            The name
        """
        return self._name

    @property
    def data_array(self):
        """Returns the underlying nixio.DataArray entity.

        Returns
        -------
        nixio.DataArray
            The nix entity that holds the trace data.
        """
        return self._data_array

    @property
    def sampling_interval(self):
        """The sampling interval of this trace.

        Returns
        -------
        float
            The sampling interval in seconds.
        """
        if self.trace_type == DataType.Event:
            logging.warning("DataTrace: sampling interval makes no sense for event traces!")
        return self._sampling_interval

    def __str__(self) -> str:
        str = f"Name: {self._name}\tid: {self._id}\ntype: {self._type}\t data type: {self._trace_type}\t shape {self._shape}\n maximum time: {self._max_time}"
        return str

    def __repr__(self) -> str:
        return "DataTrace (Name: %r, DataArray: %r, DataType: %r)" % (self.name, self.data_array.id, self.trace_type)
