import numpy as np
import nixio as nix

from IPython import embed


class Stimulus(object):

    def __init__(self, repro_run: rlxnix.ReproRun, stimulus_mtag: nix.MultiTag, index: int) -> None:
        super().__init__(re)
        self._repro_run = repro_run
        self._mtag = stimulus_mtag
        self._index = index
