import nixio
import numpy as np
import matplotlib.pyplot as plt

from .efish_ephys_repro import EfishEphys


class Chirps(EfishEphys):
    _repro_name = "Chirps"

    def __init__(self, repro_run: nixio.Tag, traces, relacs_nix_version=1.1):
        super().__init__(repro_run, traces, relacs_nix_version=relacs_nix_version)

    @property
    def chirp_times(self):
        """ The times of the artificial chirps of a given stimulus presentation.

        Returns
        -------
        list
            The chirp times relative to stimulus onset
        str
            The unit
        """
        cts = []
        unit = ""
        for s in self.stimuli:
            metadata = s.metadata
            cts.append(metadata[s.name]["ChirpTimes"][0])
            unit = s.metadata[s.name]["ChirpTimes"][1]
        return cts, unit

    @property
    def beat_specification(self):
        """Returns the way the beat is specified. Will return either *absolute frequency* or "Relative EODf".
        In the first case the beat frequency is given by the *delta_f* property, in the latter by the *relative_eodf* property.

        Returns
        -------
        str
            the beat selection setting of the Chirps RePro.
        """
        spec = self.metadata["RePro-Info"]["settings"]["beatsel"][0][0]
        return spec

    @property
    def relative_eodf(self):
        """The beat frequency specified relative to the EOD frequency of the fish.

        Returns
        -------
        float
            the releodf setting of the repro run.
        """
        rel = self.metadata["RePro-Info"]["settings"]["releodf"][0][0]
        return rel

    @property
    def delta_f(self):
        """The difference frequency to the recorded fish's EOD frequency for all stimulus presentations

        Returns
        -------
        float
            The dfs used.
        str
            the unit
        """
        df = self.metadata["RePro-Info"]["settings"]["deltaf"][0][0]
        unit = self.metadata["RePro-Info"]["settings"]["deltaf"][1]
        return df, unit

    @property
    def chirp_duration(self):
        """The chirp durations of the stimulus presentations.

        Returns
        -------
        float
            The chirp duration.
        str
            the unit
        """
        cd = self.metadata["RePro-Info"]["settings"]["chirpwidth"][0][0]
        unit = self.metadata["RePro-Info"]["settings"]["chirpwidth"][1]
        return cd, unit

    @property
    def chirp_size(self):
        """The size of the frequency excursion of the chirp.

        Returns
        -------
        list
            List containing the chirp size for each stimulus presentation.
        str
            the unit
        """
        cs = self.metadata["RePro-Info"]["settings"]["chirpsize"][0][0]
        unit = self.metadata["RePro-Info"]["settings"]["chirpsize"][1]
        return cs, unit

    def _plot_axis(self, axis, x_data, y_data, spikes, chirp_times, ylabel):
        axis.plot(x_data, y_data, lw=0.5, color="tab:blue", label="voltage")
        axis.scatter(spikes, np.ones_like(spikes) * np.max(y_data), s=10, marker="*", c="tab:green", label="spikes")
        axis.scatter(chirp_times, np.ones_like(chirp_times) * np.min(y_data), s=20, marker="o", c="tab:red", label="chirps")
        axis.set_ylabel(ylabel)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.set_xlim([x_data[0], x_data[-1]])

    def plot_overview(self, stimulus_index=0, filename=None):
        """[summary]

        Parameters
        ----------
        stimulus_index : int, optional
            The stimulus index, by default 0
        filename: str, optional
            The filename for the figure. If not given, the plot will be shown. By default None

        """
        spikes = self.spikes(stimulus_index=stimulus_index)
        voltage, time = self.membrane_voltage(stimulus_index=stimulus_index)
        eod, eod_time = self.local_eod(stimulus_index=stimulus_index)
        stim, stim_time = self.stimulus_output(stimulus_index=stimulus_index)
        chirp_times, _ = self.chirp_times
        c_times = chirp_times[stimulus_index]

        fig, axes = plt.subplots(ncols=1, nrows=3, sharex="all")
        self._plot_axis(axes[0], time, voltage, spikes, c_times, "voltage [mV]")
        axes[0].legend(fontsize=7, ncol=3, loc=(0.5, 1.05))
        self._plot_axis(axes[1], eod_time, eod, spikes, c_times, "voltage [mV]")
        self._plot_axis(axes[2], stim_time, stim, spikes, c_times, "voltage [mV]")
        axes[-1].set_xlabel("time [s]")

        if filename is not None:
            fig.savefig(filename)
            plt.close()
        else:
            plt.show()
