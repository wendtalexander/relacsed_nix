import os
import nixio
import logging
import numpy as np
from enum import Enum, auto

from .util import convert_path
from .mappings import DataType, type_map


class SegmentType(Enum):
    ReproRun = "ReproRun"
    StimulusSegment = "StimulusSegment"

    def __str__(self):
        return self.name


class DataLink(object):
    """Instances of this class contain all information needed to uniquely identify a data segment and read it from file.
    """
    def __init__(self, dataset_name : str, block_id : str, tag_id : str, segment_type : SegmentType,
                 start_time : float, stop_time : float, index=None, max_before= 0.0, max_after=0.0, metadata=None, relacs_nix_mapping_version=1.1) -> None:
        """[summary]

        Parameters
        ----------
        dataset_name : str
            [description]
        block_id : str
            [description]
        tag_id : str
            [description]
        segment_type : SegmentType
            [description]
        start_time : float
            [description]
        stop_time : float
            [description]
        index : int, optional
            [description], by default None
        max_before : float, optional
            The maximum time before that can be read. Defaults to 0.0
        max_after : float, optional
            The maximum time after stimulus onset that can be read. Defaults to 0.0
        metadata : str, optional
            The metadata belonging to the data segment. e.g. in JSON
        relacs_nix_mapping_version: float
            The mapping version from relacs to nix files.
        """
        super().__init__()
        self._dataset_name = dataset_name
        self._block_id = block_id
        self._tag_id = tag_id
        self._segment_type = segment_type
        self._start_time = start_time
        self._stop_time = stop_time
        assert(self._stop_time > self._start_time)
        self._index = index
        self._max_before = max_before
        self._max_after = max_after
        self._metadata = metadata
        self._mapping_version = relacs_nix_mapping_version

    @property
    def dataset(self):
        return self._dataset_name

    @property
    def block_id(self):
        return self._block_id

    @property
    def tag_id(self):
        return self._tag_id

    @property
    def segment_type(self):
        return self._segment_type

    @property
    def start_time(self):
        return self._start_time

    @property
    def stop_time(self):
        return self._stop_time

    @property
    def index(self):
        return self._index

    @property
    def mapping_version(self):
        return self._mapping_version

    @property
    def max_before(self):
        return self._max_before

    @property
    def max_after(self):
        return self._max_after

    @property
    def metadata(self):
        return self._metadata

    def __repr__(self) -> str:
        repr = "DataLink for {type}, {id} of dataset {name} from {start:.4f}s to {stop:.4f}s at {self_id}"
        return repr.format(type=str(self.segment_type), id=self.tag_id, name=self.dataset,
                           start=self.start_time, stop=self.stop_time, self_id=hex(id(self)))

def load_data_segment(data_link : DataLink, trace_name : str, before=0.0, after=0.0,
                      data_location="."):
    """[summary]

    Parameters
    ----------
    data_link : DataLink
        [description]
    trace_name : str
        [description]
    before : float, optional
        [description], by default 0.0
    after : float, optional
        [description], by default 0.0
    data_location : str, optional
        [description], by default ".", i.e. the present working directory

    Returns
    -------
    [type]
        [description]
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
    if data_link.segment_type == SegmentType.ReproRun:
        if data_link.tag_id not in block.tags:
            logging.error(f"Tag with id {data_link.tag_id} is not found in {block}!")
            return None, None
        tag = block.tags[data_link.tag_id]
    else:
        if data_link.tag_id not in block.multi_tags:
            logging.error(f"MultiTag with id {data_link.tag_id} is not found in {block}!")
            return None, None
        tag = block.multi_tag[data_link.tag_id]

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

    logging.debug(f"Reading data from data array {data_array} in the interval {start_time}, {stop_time}.")
    data = data_array.get_slice([start_time], [stop_time], nixio.DataSliceMode.Data)[:]
    time = None
    if trace_type == continuous_type:
        time = np.array(data_array.dimensions[0].axis(len(data)))
        time -= before
    else:
        data -=  data_link.start_time
    
    nf.close()  # all done, close the file
    return data, time