import warnings
import numpy as np

from ...repro import ReProRun
from ...mappings import DataType, type_map

from IPython.terminal.embed import embed



class Baseline(ReProRun):
    _repro_name = "BaselineActivity"

    def __init__(self, repro_run, relacs_nix_version=1.1, spikes_trace="Spikes-1",
                 eod_trace="EOD", eod_event_trace="EOD_events") -> None:
        super().__init__(repro_run, relacs_nix_version)
        self._spikes = None
        self._local_eod = None
        self._global_eod = None
        self._global_eod_times = None
        self.spikes_trace = spikes_trace
        self.eod_trace = eod_trace
        self.eod_event = eod_event_trace
        self._scan_tag()

    def _load_data_trace(self, name, var):
        if var is None:
            if name in self.repro_tag.references:
                var = self.repro_tag.retrieve_data(name)[:]
            else:
                warnings.warn("Could not load {name} data trace!", UserWarning)

    def _load_event_data(self, name, var):
        if var is None:
            if name in self.repro_tag.references:
                self._spikes = self.repro_tag.retrieve_data(name)[:] - self._start_time    
            else:
                warnings.warn("Could not load {name} event data!", UserWarning)

    def _scan_tag(self):
        sampled_data = [da for da in self.repro_tag.references if type_map[self._mapping_version][DataType.continuous] in da.type]
        self._sampling_interval = -1 if len(sampled_data) == 0 else sampled_data[0].dimensions[0].sampling_interval
        """
        if self.spikes_trace in self.repro_tag.references:
            self._spikes = self.repro_tag.retrieve_data(self.spikes_trace)[:] - self._start_time
        if "LocalEOD-1" in self.repro_tag.references:
            self._local_eod = self.repro_tag.retrieve_data("LocalEOD-1")[:]
        if self.eod_trace in self.repro_tag.references:
            self._global_eod = self.repro_tag.retrieve_data(self.eod_trace)[:]
        if self.eod_event in self.repro_tag.references:
            self._global_eod_times = self.repro_tag.retrieve_data(self.eod_event)[:] - self._start_time
        """

    @property
    def spikes(self):
        self._load_event_data(self.spikes_trace, self._spikes)
        return self._spikes

    @property
    def eod_times(self):
        self._load_event_data(self.eod_event, self._global_eod_times)
        return self._global_eod_times

    @property
    def baseline_rate(self):
        return len(self.spikes) / self.duration

    @property
    def baseline_cv(self):
        if self._spikes is None or len(self._spikes) == 0:
            UserWarning("there are no baseline spikes")
            return 0.0
        isis = np.diff(self._spikes)
        return np.std(isis) / np.mean(isis)

    @property
    def eod_frequency(self):
        return len(self._global_eod_times) / self._duration

    def serial_correlation(self, max_lags=50):
        if self.spikes is None or len(self.spikes) < max_lags:
            return None
        isis = np.diff(self.spikes)
        unbiased = isis - np.mean(isis, 0)
        norm = sum(unbiased ** 2)
        a_corr = np.correlate(unbiased, unbiased, "same") / norm
        a_corr = a_corr[int(len(a_corr) / 2):]
        return a_corr[:max_lags]
