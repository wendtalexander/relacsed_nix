import numpy as np
from enum import Enum
import matplotlib.pyplot as plt


class IntervalMode(Enum):
    """The IntervalMode defines how Timeline will search for respros.

    IntervalMode.Within: to find ReproRuns that start and end within the given interval
    IntervalMode.Embracing: to find ReproRuns that embrace the given time interval. That is, the time interval must be within the ReproRun start and end.
    """
    Within = 1
    Embracing = 2


class Timeline(object):
    """
    Class that represents the timeline of the dataset. It contains the start and end times of all repro Runs and all stimulus outputs stored in the recording.
    """
    def __init__(self, filename, repro_map, stimulus_mtags) -> None:
        super().__init__()
        self._filename = filename
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
        names : np.ndarray of str
            stimulus names
        indices : np.ndarray of int
            Stimulus indices in the respective MultiTags.
        start_times : np.ndarray of float
            Stimulus start times.
        stop_times : np.ndarray of float
            Stimulus stop times.
        """
        ind = np.where((self._stim_start_times >= interval_start) &
                       (self._stim_stop_times <= interval_stop))
        indices = self._stim_indices[ind]
        names = self._stim_names[ind]
        start_times = self._stim_start_times[ind]
        stop_times = self._stim_stop_times[ind]

        return names, indices, start_times, stop_times

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
        np.ndarray of str
            The names of the matching ReProRuns
        """
        if interval_stop is None:
            interval_stop = interval_start

        if mode == IntervalMode.Embracing:
            names = self._repro_names[(self._repro_start_times <= interval_start) &
                                      (self._repro_stop_times >= interval_stop)]
        else:
            names = self._repro_names[(self._repro_start_times >= interval_start) &
                                      (self._repro_stop_times <= interval_stop)]

        return names

    def next_stimulus_start(self, previous_stimulus_end):
        st = self._stim_start_times[self._stim_start_times > previous_stimulus_end]
        return st[0] if len(st) > 0 else None

    @property
    def min_time(self):
        return self._repro_start_times[0]

    @property
    def max_time(self):
        return self._repro_stop_times[-1]

    def __repr__(self) -> str:
        return "rlxnix.Timeline"
    
    def plot(self):
        """plots the timeline for some visual inspections.
        """
        def _update_repro_annotation(ind):
            bar_index = ind["ind"][0]
            pos = (repro_bar_centers[bar_index], 0.9)
            if pos[0] > axis.get_xlim()[-1]/2:
                repro_annotation.set_x(-20)
                repro_annotation.set_ha("right")
            else:
                repro_annotation.set_x(20)
                repro_annotation.set_ha("left")
            repro_annotation.xy = pos
            text = "{name:s}\n{start:.4f}s to {end:.4f}s".format(name=self._repro_names[bar_index],
                                                                  start=self._repro_start_times[bar_index],
                                                                  end=self._repro_stop_times[bar_index])
            repro_annotation.set_text(text)
            repro_annotation.get_bbox_patch().set_facecolor(None)
            repro_annotation.get_bbox_patch().set_alpha(0.4)
        
        def _hover(event):
            if event.button == 1:
                return
            vis = repro_annotation.get_visible()
            if event.inaxes == axis:
                cont, ind = bar_collection.contains(event)
                if cont:
                    _update_repro_annotation(ind)
                    repro_annotation.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        repro_annotation.set_visible(False)
                        fig.canvas.draw_idle()

        fig, axis = plt.subplots(ncols=1, nrows=1, figsize=(15, 2.5), constrained_layout=True)
        axis.set_title(self._filename)
        fig.canvas.mpl_connect("motion_notify_event", _hover)
        repro_extents = []
        repro_colors = []
        repro_bar_centers = []
        repro_color_map = {}
        color_map = plt.get_cmap("tab10").colors
        unique_repro_names = list(np.unique([name.split("_")[0] for name in self._repro_names]))
        for start, stop, name in zip(self._repro_start_times, self._repro_stop_times, self._repro_names):
            repro_extents.append(stop - start)
            repro_bar_centers.append(start + repro_extents[-1]/2)
            index = unique_repro_names.index(name.split("_")[0])
            repro_colors.append(color_map[index])
            repro_color_map[name] = repro_colors[-1]

        bar_collection = axis.broken_barh(xranges=list(zip(self._repro_start_times, repro_extents)),
                                          yrange=(0.5, 0.5), facecolors=repro_colors, linewidth=0.1,
                                          edgecolor="black", alpha=0.75)

        repro_annotation = axis.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points", 
                                         ha="center", bbox=dict(boxstyle="round", fc="w"), arrowprops=dict(arrowstyle="->"))
        repro_annotation.set_visible(False)

        stimulus_colors = []
        stimulus_extents = []
        for start, stop, name in zip(self._stim_start_times, self._stim_stop_times, self._stim_names):
            stimulus_extents.append(stop - start)
            r = self.find_repro_runs(start, stop, IntervalMode.Embracing)
            stimulus_colors.append(repro_color_map[r[0]])
        stim_bar_collection = axis.broken_barh(xranges=list(zip(self._stim_start_times, stimulus_extents)),
                                               yrange=(0.65, 0.2), facecolors=stimulus_colors, linewidth=0.1,
                                               edgecolor="black", alpha=1)

        axis.spines["top"].set_visible(False)
        axis.spines["left"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.set_yticks([])
        axis.set_ylim(0, 1.5)
        axis.set_xlabel("time [s]")

        plt.show()
