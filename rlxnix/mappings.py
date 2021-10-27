from enum import Enum

class DataType(Enum):
      Continuous = 0
      Event = 1


type_map = {1.0: {DataType.Event: "nix.events.positions",
                  DataType.Continuous: "nix.data.sampled"},
            1.1: {DataType.Event: "relacs.data.event",
                  DataType.Continuous: "relacs.data.sampled"}
            }