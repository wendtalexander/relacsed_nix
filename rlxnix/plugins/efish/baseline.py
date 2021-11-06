import logging
import numpy as np

from .efish_ephys_repro import EfishEphys


class Baseline(EfishEphys):
    _repro_name = "BaselineActivity"

    def __init__(self, repro_run, traces, relacs_nix_version=1.1) -> None:
        super().__init__(repro_run, traces, relacs_nix_version)

    @property
    def baseline_rate(self):
        return len(self.spikes()) / self.duration

    @property
    def baseline_cv(self):
        spikes = self.spikes()
        if spikes is None or len(spikes) == 0:
            logging.warn("There are no baseline spikes")
            return 0.0
        isis = np.diff(spikes)
        return np.std(isis) / np.mean(isis)

    @property
    def eod_frequency(self):
        return len(self.eod_times()) / self._duration

    def serial_correlation(self, max_lags=50):
        if self.spikes() is None or len(self.spikes()) < max_lags:
            return None
        isis = np.diff(self.spikes())
        unbiased = isis - np.mean(isis, 0)
        norm = sum(unbiased ** 2)
        a_corr = np.correlate(unbiased, unbiased, "same") / norm
        a_corr = a_corr[int(len(a_corr) / 2):]
        return a_corr[:max_lags]
