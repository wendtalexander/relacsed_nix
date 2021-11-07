from enum import Enum

import nixio
import nixio


class DataType(Enum):
      Continuous = 0
      Event = 1
      StimulusSegment = 2


type_map = {1.0: {DataType.Event: "nix.events.position",
                  DataType.Continuous: "nix.data.sampled",
                  DataType.StimulusSegment: "nix.event.stimulus"},
            1.1: {DataType.Event: "relacs.data.event",
                  DataType.Continuous: "relacs.data.sampled",
                  DataType.StimulusSegment: "relacs.stimulus"}
            }


def tag_start_and_extent(tag, index, mapping_version):
    start_time = None
    duration = None
    if isinstance(tag, nixio.MultiTag):
        if mapping_version == 1.0:
            start_time = tag.positions[index][0]
            duration = tag.extents[index][0] if tag.extents else 0.0
        else:
            start_time = tag.positions[index, 0][0]
            duration = tag.extents[index, 0][0] if tag.extents else 0.0
    elif isinstance(tag, nixio.Tag):
        start_time = tag.position[0]
        duration = tag.extent[0] if tag.extent else 0.0
    return start_time, duration
