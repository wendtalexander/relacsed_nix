import os
import nixio
import logging
import numpy as np
import pandas as pd
from enum import Enum
from typing import Optional, Tuple

from .util import convert_path
from .mappings import DataType, type_map

from IPython import embed
class SegmentType(Enum):
    ReproRun = "ReproRun"
    StimulusSegment = "StimulusSegment"

    def __str__(self):
        return self.name


class DataLink(object):
    """Instances of this class contain all information needed to uniquely identify a data segment and read it from a NIX file.
    """
    _cols = ["dataset_name", "block_id", "tag_id", "segment_type", "start_time", "stop_time", "index", "max_before", "max_after", "mapping_version", "metadata"]

    
    def __init__(self, dataset_name : str, block_id : str, tag_id : str, segment_type : SegmentType,
                 start_time : float, stop_time : float, index=None, max_before= 0.0, max_after=0.0, metadata=None, mapping_version=1.1) -> None:
        """DataLink object that uniquely identifies a segment of the data in a relacs recorded nix file.

        Parameters
        ----------
        dataset_name : str
            The name of the dataset (without any path information)
        block_id : str
            The id of the nixio.Block entity that contains the data segment.
        tag_id : str
            The id of the nixio.Tag or nixio.MultiTag entity that tags the data.
        segment_type : SegmentType
            The segment type specifies whether the given DataLink points to a stimulus segment or the full repro run.
        start_time : float
            The start time of the segment (in data time, not real time).
        stop_time : float
            The stop time of the segment (again, data time, not real time).
        index : int, optional
            The stimulus index, only needed for stimulus segments, by default None
        max_before : float, optional
            The maximum time before that can be read. Defaults to 0.0
        max_after : float, optional
            The maximum time after stimulus onset that can be read. Defaults to 0.0
        metadata : str, optional
            The metadata belonging to the data segment. e.g. in JSON
        mapping_version: float
            The mapping version from relacs to nix files.
        
        Raises
        ------
        ValueError
            If stop_time is less or equal start_time
        """
        super().__init__()
        self._dataset_name = dataset_name
        self._block_id = block_id
        self._tag_id = tag_id
        self._segment_type = segment_type
        self._start_time = start_time
        self._stop_time = stop_time
        if self._stop_time <= self._start_time:
            logging.error(f"DataLink: trying to create a DataLink to a {self._segment_type:s} with the stop time {self._stop_time} less or equal to the {self._start_time}!")
            raise ValueError(f"DataLink: trying to create a DataLink to a {self._segment_type:s} with the stop time {self._stop_time} less or equal to the {self._start_time}!")
        self._index = index
        self._max_before = max_before
        self._max_after = max_after
        self._metadata = metadata
        self._mapping_version = mapping_version

    @property
    def dataset_name(self)->str:
        return self._dataset_name

    @property
    def block_id(self)->str:
        return self._block_id

    @property
    def tag_id(self)->str:
        return self._tag_id

    @property
    def segment_type(self)->str:
        return str(self._segment_type)

    @property
    def start_time(self)->float:
        return self._start_time

    @property
    def stop_time(self)->float:
        return self._stop_time

    @property
    def index(self)->Optional[int]:
        return self._index

    @property
    def mapping_version(self)->float:
        return self._mapping_version

    @property
    def max_before(self)->float:
        return self._max_before

    @property
    def max_after(self)->float:
        return self._max_after

    @property
    def metadata(self)->dict:
        return self._metadata

    @property
    def mapping_version(self):
        return self._mapping_version

    @staticmethod
    def columns()->list:
        return DataLink._cols

    def to_pandas(self)->pd.DataFrame:
        cols = self.columns()
        values = [getattr(self, c) for c in cols]

        return pd.DataFrame([values], columns=cols)

    @staticmethod
    def from_pandas(data_frame : pd.DataFrame, index : int):
        """Creates a DataLink object from a row in a data_frame. E.g. from the data frame created by exporting the contents of a rlxnix.Dataset (to_pandas).

        Parameters
        ----------
        data_frame : pandas.DataFrame
            The data frame
        index : int
            The index of the respective row.

        Returns
        -------
        DataLink
            The DataLink for the entry.
        """
        if index not in data_frame.index:
            logging.error(f"from_pandas: index {index} is invalid in data_frame")
            return None
        specs = {}
        row = data_frame[data_frame.index == index]
        for c in DataLink.columns():
            if c not in data_frame.columns:
                logging.error(f"DataLink.from_pandas: required column {c} not in data frame!")
                raise ValueError(f"DataLink.from_pandas: required column {c} not in data frame!")
            specs[c] = row[c].values[0]
        link = DataLink(**specs)

        return link

    def __repr__(self) -> str:
        repr = "DataLink for {type}, {id} of dataset {name} from {start:.4f}s to {stop:.4f}s at {self_id}"
        return repr.format(type=str(self.segment_type), id=self.tag_id, name=self.dataset_name,
                           start=self.start_time, stop=self.stop_time, self_id=hex(id(self)))


def from_pandas(data_frame: pd.DataFrame, index: Optional[int] = None, segment_type : Optional[SegmentType] =None) -> DataLink:
    """Creates a DataLink object from a row in a data_frame. E.g. from the data frame created by exporting the contents of a rlxnix.Dataset (to_pandas).

    Parameters
    ----------
    data_frame : pandas.DataFrame
        The data frame
    index : int, optional
        The index of the respective row. If None all entries will be converted.
    segment_type : SegmentType, optional
        If index is not specified one can restrict the selection based on the SegmentType. Defaults to None, that is, all entries will be selected.
    
    Returns
    -------
    DataLink or list of DataLink entities
        The DataLink for the entry(entries).
    """
    if index is None:
        if segment_type is not None:
            df = data_frame[data_frame.segment_type == str(segment_type)]
            return [DataLink.from_pandas(df, index) for index in df.index]
        else:
            return [DataLink.from_pandas(data_frame, index) for index in data_frame.index]
    else:
        return DataLink.from_pandas(data_frame, index)


def load_data_segment(data_link : DataLink, trace_name : str, before=0.0, after=0.0,
                      data_location=".")->Tuple[np.ndarray, Optional[np.ndarray]]:
    """Loads the data specified from the DataLink (link to a stimulus or repro run segment) and the trace name. Optionally one can ask to return more data by specifying a before and/or after time. If these are invalid (because there was no data recorded before or after the respective segment) they will be reset to zero or the maximal possible values. 

    The DataLink object contains only the name of the dataset not its location of the hard drive. The data location must be specified, if the dataset is not located in the present directory.

    Parameters
    ----------
    data_link : DataLink
        The DataLink object pointing at the selected data segment.
    trace_name : str
        The name of the recorded signal that should be read.
    before : float, optional
        If possible, read data from before segment start, by default 0.0
    after : float, optional
        If possible, also read the data after segment stop, by default 0.0
    data_location : str, optional
        The folder where to find the dataset, by default ".", i.e. the present working directory

    Returns
    -------
    np.ndarray
        The data read from the trace (trace_name).
    np.ndarray or None
        The respective time axis if the data trace is continuous data trace, None, otherwise.
    """
    converted_path = convert_path(data_link.dataset)
    filename  = converted_path.split(os.sep)[-1]
    converted_path = os.sep.join((data_location, filename))

    if not os.path.exists(converted_path):
        logging.error(f"Nix file {filename} could not be read from path {converted_path}!")
        return None, None

    nf = nixio.File.open(converted_path, nixio.FileMode.ReadOnly)
    if data_link.block_id not in nf.blocks:
        logging.error(f"Block with id {data_link.block_id} is not found in {filename}!")
        return None, None
    block = nf.blocks[data_link.block_id]

    tag = None
    if SegmentType[data_link.segment_type] is SegmentType.ReproRun:
        if data_link.tag_id not in block.tags:
            logging.error(f"Tag with id {data_link.tag_id} is not found in {block}!")
            return None, None
        tag = block.tags[data_link.tag_id]
    elif SegmentType[data_link.segment_type] is SegmentType.StimulusSegment:
        if data_link.tag_id not in block.multi_tags:
            logging.error(f"MultiTag with id {data_link.tag_id} is not found in {block}!")
            return None, None
        tag = block.multi_tags[data_link.tag_id]
    else:
        logging.error(f"load_data_segment: Segment type ({data_link.segment_type}) is invalid! Allowed values are {SegmentType.StimulusSegment} or {SegmentType.ReproRun}!")
        return None, None

    if trace_name not in tag.references:
        logging.error(f"The given tag does not refer to a trace {trace_name}! Or a trace with that name does not exist (traces are: {tag.references})!")
        return None, None
    data_array = tag.references[trace_name]
    t = data_array.type

    event_type = type_map[data_link.mapping_version][DataType.Event]
    continuous_type = type_map[data_link.mapping_version][DataType.Continuous]
    if (event_type not in t) and (continuous_type not in t):
        logging.error(f"Can only process event ({event_type}) or continuous ({continuous_type}) data! Found type: {data_array.type}!")
        return None, None
    trace_type = event_type if event_type in t else continuous_type

    start_time = data_link.start_time
    if before > data_link.max_before:
        logging.warning(f"The given before time {before} exceeds the maximum valid before time {data_link.max_before}. Set to maximum valid time!")
        start_time -= data_link.max_before
    else:
        start_time -= before
    
    stop_time = data_link.stop_time
    if after > data_link.max_after:
        logging.warning(f"The given after time {before} exceeds the maximum valid after time {data_link.max_after}. Set to maximum valid time!")
        stop_time += data_link.max_after
    else:
        stop_time += after
    extent = stop_time - start_time
    logging.info(f"Reading data from data array {data_array} in the interval {start_time}, {stop_time}.")
    data = data_array.get_slice([start_time], [extent], nixio.DataSliceMode.Data)[:]
    time = None
    if trace_type == continuous_type:
        time = np.array(data_array.dimensions[0].axis(len(data)))
        time -= before
    else:
        data -=  data_link.start_time
    
    nf.close()  # all done, close the file
    return data, time