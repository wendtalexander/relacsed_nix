import numpy as np
from enum import Enum


class IntervalMode(Enum):
    Within = 1
    Embracing = 2


class Timeline(object):
    """
    Class that represents the timeline of the dataset. It contains the start and end times of all repro Runs and all stimulus outputs stored in the recording.
    """
    def __init__(self, repro_map, stimulus_mtags) -> None:
        super().__init__()
        self._repro_start_times = np.zeros(len(repro_map))
        self._repro_stop_times = np.zeros_like(self._repro_start_times)
        self._repro_names = np.empty_like(self._repro_start_times, dtype=object)
        self._stim_start_times = None
        self._stim_stop_times = None
        self._stim_indices = None
        self._stim_names = None
        self._scan_repro_times(repro_map)
        self._scan_stimulus_times(stimulus_mtags)

    def _scan_repro_times(self, repro_map):
        for i, k in enumerate(repro_map.keys()):
            rd = repro_map[k]
            self._repro_names[i] = rd.name
            self._repro_start_times[i] = rd.start_time
            self._repro_stop_times[i] = self._repro_start_times[i] + rd.duration
        ind = np.argsort(self._repro_start_times)
        self._repro_start_times = self._repro_start_times[ind]
        self._repro_stop_times = self._repro_stop_times[ind]
        self._repro_names = self._repro_names[ind]

    def _total_stim_count(self, mtags):
        stim_count = 0
        for mt in mtags:
            stim_count += mt.positions.shape[0]
        return stim_count

    def _scan_stimulus_times(self, mtags):
        total_stim_count = self._total_stim_count(mtags)
        self._stim_start_times = np.zeros(total_stim_count)
        self._stim_stop_times = np.zeros_like(self._stim_start_times)
        self._stim_names = np.empty_like(self._stim_start_times, dtype=object)
        self._stim_indices = np.zeros_like(self._stim_start_times, dtype=int)
        index = 0
        for mt in mtags:
            if "relacs.stimulus" not in mt.type:
                continue
            for i in range(mt.positions.shape[0]):
                start = mt.positions[i, 0]
                ext = mt.extents[i, 0] if mt.positions else 0.0
                self._stim_start_times[index] = start
                self._stim_stop_times[index] = start + ext
                self._stim_indices[index] = i
                self._stim_names[index] = mt.name
                index += 1

        ind = np.argsort(self._stim_start_times)
        self._stim_start_times = self._stim_start_times[ind]
        self._stim_stop_times = self._stim_stop_times[ind]
        self._stim_indices = self._stim_indices[ind]
        self._stim_names = self._stim_names[ind]

    @property
    def stimuli(self):
        """Returns the stimuli that were run in chronological order. 

        Returns
        -------
        start_times : list of float
            The stimulus start times in seconds
        stop_times : list of float
            The stimulus stop times in seconds
        stim_indices : list of int
            The index of the stimulus in the respective MultiTag.
        stim_names : list of str
            The names of the respective MultiTags            
        """        
        return self._stim_start_times, self._stim_stop_times, self._stim_indices, self._stim_names

    def find_stimuli(self, interval_start, interval_stop):
        """Find the stimuli that happen in a given interval. Intervals are given in seconds. Stimuli with start times >= interval_start and stop times <= interval_stop are considered. 

        Parameters
        ----------
        interval_start : float
            The interval start time in seconds
        interval_stop : float
            The interval stop time.

        Returns
        -------
        names : list of str
            stimulus names
        indices : list of int
            Stimulus indices in the respective MultiTags.
        """        
        indices = []
        names = []
        for start, stop, index, name in zip(self._stim_start_times, self._stim_stop_times, self._stim_indices, self._stim_names):
            if start >= interval_start and stop <= interval_stop:
                indices.append(index)
                names.append(name)
        return names, indices

    def find_repro_runs(self, interval_start, interval_stop=None, mode=IntervalMode.Embracing):
        """Find the ReproRuns that happen within a given interval or that embrace a give interval.

        Parameters
        ----------
        interval_start : float
            start time of the considered interval
        interval_stop : float, optional
            stop time of the interval, if None, stop is set to start. Defaults to None
        mode : IntervalMode, optional
            Defines whether the ReproRun must be within the given interval or whether the ReproRun must embrace the given interval, by default IntervalMode.Embracing

        Returns
        -------
        list of str
            The names of the matching ReProRuns
        """        
        names = []
        if interval_stop is None:
            interval_stop = interval_start
        
        for start, stop, name in zip(self._repro_start_times, self._repro_stop_times, self._repro_names):
            if mode == IntervalMode.Embracing:
                if start <= interval_start and stop >= interval_stop:
                    names.append(name)
            else:
                if start >= interval_start and stop <= interval_stop:
                    names.append(name)
    
        return names

    @property
    def min_time(self):
        return self._repro_start_times[0]

    @property
    def max_time(self):
        return self._repro_stop_times[-1]
    