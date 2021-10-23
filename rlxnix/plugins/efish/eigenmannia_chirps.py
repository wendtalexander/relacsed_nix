import nixio
from ...repro import ReProRun

from IPython.terminal.embed import embed


class EigenmanniaChirps(ReProRun):
    _repro_name = "EigenmanniaChirps"

    def __init__(self, repro_run: nixio.Tag, relacs_nix_version=1.1):
        super().__init__(repro_run, relacs_nix_version=relacs_nix_version)
    
    def _check_stimulus(self, stimulus_index):
        if stimulus_index >= len(self.stimuli) or stimulus_index < 0:
            raise IndexError(f"Stimulus index {stimulus_index} is out of bounds for number of stimuli {len(self.stimuli)}")

    def _check_trace(self, trace_name):
        if trace_name not in self._tag.references:
            raise ValueError(f"Trace {trace_name} not found!")

    def spikes(self, stimulus_index=None, trace_name="Spikes-1"):
        self._check_trace(trace_name)
        if stimulus_index is not None:
            self._check_stimulus(stimulus_index)
            return self.stimuli[stimulus_index].trace_data(trace_name)[0]
        else:
            return self.trace_data(trace_name)[0]

    def local_eod(self, stimulus_index=None, trace_name="LocalEOD-1"):
        self._check_trace(trace_name)
        
        if stimulus_index is not None:
            self._check_stimulus(stimulus_index)
            return self.stimuli[stimulus_index].trace_data(trace_name)
        else:
            return self.trace_data(trace_name)
    
    def chirp_times(self, stimulus_index=0):
        self._check_stimulus(stimulus_index)
        stimulus = self.stimuli[stimulus_index]
        metadata = stimulus.metadata
        cts = metadata[stimulus.name]["ChirpTimes"][0]
        return cts

    @property
    def chirp_type(self):
        return self.metadata["RePro-Info"]["settings"]["chirptype"]

    @property
    def delta_f(self):
        dfs = []
        unit = ""
        for s in self.stimuli:
            dfs.append(s.metadata[s.name]["deltaf"][0])
            unit = s.metadata[s.name]["deltaf"][1]
        return dfs, unit

    @property
    def chirp_duration(self):
        cds = []
        unit = ""
        for s in self.stimuli:
            cds.append(s.metadata[s.name]["chirp duration"][0])
            unit = s.metadata[s.name]["chirp duration"][1]
        return cds, unit