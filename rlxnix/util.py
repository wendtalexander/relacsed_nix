from IPython.terminal.embed import embed
import numpy as np


def nix_metadata_to_dict(section):
    info = {}
    for p in section.props:
        info[p.name] = [v for v in p.values]
    for s in section.sections:
        info[s.name] = nix_metadata_to_dict(s)
    return info


class Timeline(object):

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
        return self._stim_start_times, self._stim_stop_times, self._stim_indices, self._stim_names

    def find_stimuli(self, interval_start, interval_stop):
        indices = []
        names = []
        for start, stop, index, name in zip(self._stim_start_times, self._stim_stop_times, self._stim_indices, self._stim_names):
            if start >= interval_start and stop < interval_stop:
                indices.append(index)
                names.append(name)
        return names, indices
    
    @property
    def min_time(self):
        return self._repro_start_times[0]

    @property
    def max_time(self):
        return self._repro_stop_times[-1]
    