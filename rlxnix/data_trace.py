from .mappings import DataType, type_map


class DataTrace(object):
    
    def __init__(self, data_array, mapping_version=1.1) -> None:
        super().__init__()
        event_type = type_map[mapping_version][DataType.event]
        continuous_type = type_map[mapping_version][DataType.continuous]
        t = data_array.type
        if (event_type not in t) and (continuous_type not in t):
            raise ValueError(f"DataTrace not valid to dataArrray of type {data_array.type}!")
        self._data_array = data_array
        self._name = data_array.name
        self._id = data_array.id
        self._type = data_array.type
        self._trace_type = DataType.continuous if continuous_type in data_array.type else DataType.event
        self._shape = data_array.shape
        if self._trace_type == DataType.event:
            self._max_time = data_array[-1]
        else:
            self._max_time = self._shape[0] * data_array.dimensions[0].sampling_interval

    @property
    def trace_type(self):
        return self._trace_type

    @property
    def maximum_time(self):
        return self._max_time

    @property
    def shape(self):
        return self._shape
    
    @property
    def name(self):
        return self._name

    @property
    def data_array(self):
        return self._data_array

    def __str__(self) -> str:
        str = f"Name: {self._name}\tid: {self._id}\ntype: {self._type}\t data type: {self._trace_type}\t shape {self._shape}\n maximum time: {self._max_time}"
        return str
    
    def __repr__(self) -> str:
        return super().__repr__()