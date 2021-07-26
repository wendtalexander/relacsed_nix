import nixio

class RePro(object):

    def __init__(self, repro_run: nixio.Tag, relacs_nix_version=1.1):
        super().__init__()
        self._repro_run = repro_run
        self._relacs_nix_version = relacs_nix_version
        self._start_time = repro_run.position[0]
        self._duration = repro_run.extent[0]

    @property
    def start_time(self):
        return self._start_time

    @property
    def duration(self):
        return self._duration
    
    @property
    def repro_tag(self):
        return self._repro_run