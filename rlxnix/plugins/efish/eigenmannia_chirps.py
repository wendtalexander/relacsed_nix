import nixio
import numpy as np
import matplotlib.pyplot as plt

from ...repro import ReProRun
from ...mappings import DataType


class EigenmanniaChirps(ReProRun):
    _repro_name = "EigenmanniaChirps"

    def __init__(self, repro_run: nixio.Tag, traces, relacs_nix_version=1.1):
        super().__init__(repro_run, traces, relacs_nix_version=relacs_nix_version)
    
    def _check_stimulus(self, stimulus_index):
        if stimulus_index >= len(self.stimuli) or stimulus_index < 0:
            raise IndexError(f"Stimulus index {stimulus_index} is out of bounds for number of stimuli {len(self.stimuli)}")

    def _check_trace(self, trace_name, data_type=DataType.Continuous):
        if trace_name not in self._tag.references:
            raise ValueError(f"Trace {trace_name} not found!")
        trace = self._trace_map[trace_name]
        if trace.trace_type != data_type:
            raise ValueError(f"Data type of trace {trace.name} does not match expected data type (expected: {data_type}, found: {trace.trace_type}).")        

    def spikes(self, stimulus_index=None, trace_name="Spikes-1"):
        """Return the spike times for the whole repro run or during a certain stimulus presentation

        Parameters
        ----------
        stimulus_index : int, optional
            The stimulus index. If None, the spikes of the whole repro run will be read from file. By default None.
        trace_name : str, optional
            The name of the spikes event trace, by default "Spikes-1"

        Returns
        -------
        numpy ndarray
            The spike times in seconds. Times are relative to stimulus onset.
        """
        self._check_trace(trace_name, DataType.Event)
        if stimulus_index is not None:
            self._check_stimulus(stimulus_index)
            return self.stimuli[stimulus_index].trace_data(trace_name)[0]
        else:
            return self.trace_data(trace_name)[0]

    def local_eod(self, stimulus_index=None, trace_name="LocalEOD-1"):
        """Return the local eod measurement for the whole repro run or during a certain stimulus presentation.

        Parameters
        ----------
        stimulus_index :  int, optional
            The stimulus index. If None, the spikes of the whole repro run will be read from file. By default None.
        trace_name : str, optional
            The name of the spikes event trace, by default "LocalEOD-1"

        Returns
        -------
        np.ndarray 
            the local eod data
        np.ndarray
            the respective time axis
        """
        self._check_trace(trace_name, data_type=DataType.Continuous)
        
        if stimulus_index is not None:
            self._check_stimulus(stimulus_index)
            return self.stimuli[stimulus_index].trace_data(trace_name)
        else:
            return self.trace_data(trace_name)

    def membrane_voltage(self, stimulus_index=None, trace_name="V-1"):
        """Returns the membrane potential measurement for the whole repro run or during a certain stimulus presentation.

        Parameters
        ----------
        stimulus_index : int, optional
            The stimulus index. If None, the voltage trace of the whole repro run will be read from file. By default None.
        trace_name : str, optional
            The name of the membrane voltage trace, by default "V-1"

        Returns
        -------
        np.ndarray 
            the membrane potential
        np.ndarray
            the respective time axis
        """
        self._check_trace(trace_name, data_type=DataType.Continuous)
        
        if stimulus_index is not None:
            self._check_stimulus(stimulus_index)
            return self.stimuli[stimulus_index].trace_data(trace_name)
        else:
            return self.trace_data(trace_name)

    def stimulus_output(self, stimulus_index=None, trace_name="GlobalEFieldStimulus"):
        """Returns the recorded stimulus trace for the whole repro run or during a certain stimulus presentation.

        Parameters
        ----------
        stimulus_index : int, optional
            The stimulus index. If None, the stimulus trace of the whole repro run will be read from file. By default None.
        trace_name : str, optional
            The name of the recorded trace, by default "GlobalEFieldStimulus"

        Returns
        -------
        np.ndarray 
            the stimulus trace
        np.ndarray
            the respective time axis
        """
        self._check_trace(trace_name, data_type=DataType.Continuous)
        
        if stimulus_index is not None:
            self._check_stimulus(stimulus_index)
            return self.stimuli[stimulus_index].trace_data(trace_name)
        else:
            return self.trace_data(trace_name)

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
    def chirp_type(self):
        """The type of the simulated chirp, e.g. Type A or Type B

        Returns
        -------
        str
            The type
        """
        return self.metadata["RePro-Info"]["settings"]["chirptype"][0][0]

    @property
    def delta_f(self):
        """The difference frequency to the recorded fish's EOD frequency for all stimulus presentations

        Returns
        -------
        list
            List containing the dfs
        str
            the unit
        """
        dfs = []
        unit = ""
        for s in self.stimuli:
            dfs.append(s.metadata[s.name]["deltaf"][0][0])
            unit = s.metadata[s.name]["deltaf"][1]
        return dfs, unit

    @property
    def chirp_duration(self):
        """The chirp durations of the stimulus presentations.

        Returns
        -------
        list
            List containing the chirp durations
        str
            the unit
        """
        cds = []
        unit = ""
        for s in self.stimuli:
            cds.append(s.metadata[s.name]["chirp duration"][0][0])
            unit = s.metadata[s.name]["chirp duration"][1]
        return cds, unit

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

        fig, axes = plt.subplots(ncols=1, nrows=3)
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
