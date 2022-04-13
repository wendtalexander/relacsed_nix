import logging
import numpy as np

from .efish_ephys_repro import EfishEphys


class Baseline(EfishEphys):
    """Represents the run of the Baseline repro of the efish plugin-set.
    """
    _repro_name = "BaselineActivity"

    def __init__(self, repro_run, traces, relacs_nix_version=1.1) -> None:
        super().__init__(repro_run, traces, relacs_nix_version)

    @property
    def baseline_rate(self):
        """Baseline spike rate.

        Returns
        -------
        float
            The average spike rate.
        """
        return len(self.spikes()) / self.duration

    @property
    def baseline_cv(self):
        """Coefficient of variation of the interspike intervals of the baseline spike response. Depends on the spike times to be stored in the file. 
        The CV is defines as the standard deviation of the interspike intervals normalized to the average interspike interval and describes the regularity of the spontaneous spiking.
        A CV of 0 indicates perfectly regular spiking while a value of 1 is typical for random poisson spiking.

        Returns
        -------
        
            _description_
        """
        spikes = self.spikes()
        if spikes is None or len(spikes) == 0:
            logging.warn("There are no baseline spikes")
            return 0.0
        isis = np.diff(spikes)
        return np.std(isis) / np.mean(isis)

    @property
    def eod_frequency(self):
        """ Returns the EOD frequency (in Hz) of the fish. Depends on the eod times event signal to be present.

        Returns
        -------
        float or None
            the eod frequency in Hz, None if the eod times are not stored in the file.
        """
        if "eod times" not in self._signal_trace_map:
            logging.warning("EOD times are not stored in the file. You need to detect the eod times manually... ")
            return None
        return len(self.eod_times()) / self._duration

    def serial_correlation(self, max_lags=50):
        """Returns the serial correlation of the baseline interspike intervals.

        Parameters
        ----------
        max_lags : int, optional
            The number of lags to be calculated, by default 50

        Returns
        -------
        np.ndarray
            The serial correlations from lag 0 to max_lags -1
        """
        if self.spikes() is None or len(self.spikes()) < max_lags:
            return None
        isis = np.diff(self.spikes())
        unbiased = isis - np.mean(isis, 0)
        norm = sum(unbiased ** 2)
        a_corr = np.correlate(unbiased, unbiased, "same") / norm
        a_corr = a_corr[int(len(a_corr) / 2):]
        return a_corr[:max_lags]
