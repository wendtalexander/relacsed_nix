from enum import Enum

class DataType(Enum):
      continuous = 0
      event = 1


type_map = {1.0: {DataType.event: "nix.events.positions",
                  DataType.continuous: "nix.data.sampled"},
            1.1: {DataType.event: "relacs.data.event",
                  DataType.continuous: "relacs.data.sampled"}
            }