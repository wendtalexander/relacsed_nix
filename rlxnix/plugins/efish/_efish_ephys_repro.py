import nixio
import numpy as np
import matplotlib.pyplot as plt

from ...repro import ReProRun
from ...mappings import DataType


class EfishEphys(ReProRun):

    def __init__(self, repro_run: nixio.Tag, traces, relacs_nix_version=1.1):
        super().__init__(repro_run, traces, relacs_nix_version=relacs_nix_version)
    
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