import numpy as np

from ..efish.efish_ephys_repro import EfishEphys

class ReceptiveField(EfishEphys):
    _repro_name = "ReceptiveField"

    def __init__(self, repro_run, traces, relacs_nix_version=1.1) -> None:
        super().__init__(repro_run, traces, relacs_nix_version)

    @property
    def stimulus_amplitudes(self):
        ampls = []
        for stim in self.stimuli:
            if self._repro_name in stim.name:
                ampls.append(stim.feature_data(stim.name + "_ampl"))
        return np.array(ampls)

    @property
    def stimulus_frequencies(self):
        freqs = []
        for stim in self.stimuli:
            if self._repro_name in stim.name:
                freqs.append(stim.feature_data(stim.name + "_freq"))
        return np.array(freqs)

    @property
    def stimulus_durations(self):
        durations = []
        for stim in self.stimuli:
            if self._repro_name in stim.name:
                durations.append(stim.feature_data(stim.name + "_dur"))
        return np.array(durations)

    @property
    def stimulus_deltafs(self):
        dfs = []
        for stim in self.stimuli:
            if self._repro_name in stim.name:
                dfs.append(stim.feature_data(stim.name + "_deltaf"))
        return np.array(dfs)

    @property
    def fish_length(self):
        """Fish length in mm

        Returns
        -------
        float
            the fish's body length
        """
        length = 0.0
        head = self.head_position
        tail = self.tail_position
        length = np.sqrt((tail[1]-head[1])**2+(tail[2]-head[2])**2)

        return length

    @property
    def head_position(self):
        """Fish head position in mm relative to robot origin.
        Note! Robot coordinate system is rotated. x > depth, y > length, z > height in fish coordinates.

        Returns
        -------
        np.array
            fish head position in [x, y, z] positions in robot coordinates!
        """
        position = np.zeros(3)
        cell_mdata = self.repro_tag.file.find_sections(lambda s: s.name == "Cell properties")
        if len(cell_mdata) > 0 and "FishHeadPosition" in cell_mdata[0]:
            position = np.array(list(map(float, cell_mdata[0]["FishHeadPosition"][1:-1].split(","))))

        return position

    @property
    def tail_position(self):
        """Fish tail position in mm relative to robot origin.
        Note! Robot coordinate system is rotated. x > depth, y > length, z > height in fish coordinates.

        Returns
        -------
        np.array
            fish tail position in [x, y, z] positions in robot coordinates!
        """
        position = np.zeros(3)
        cell_mdata = self.repro_tag.file.find_sections(lambda s: s.name == "Cell properties")
        if len(cell_mdata) > 0 and "FishTailPosition" in cell_mdata[0]:
            position = np.array(list(map(float, cell_mdata[0]["FishTailPosition"][1:-1].split(","))))

        return position

    @property
    def stimulus_positions(self):
        """Stimulus positions relative to fish head position. Given in mm.
        Note! x is now the rostro-caudal axis of the fish, y is the dorso-ventral axis, and z the left right axis.
        (0, 0, 0) would be the tip of the snout at midline height.

        Returns:
            x, y, z np.array
                The x, y, and z coordinates of the 
        """
        x, y, z = [], [], []

        for stim in self.stimuli:
            name = stim.name
            if self._repro_name not in name:
                continue
            x.append(stim.feature_data(name + "_x_pos"))
            y.append(stim.feature_data(name + "_y_pos"))
            z.append(stim.feature_data(
                name + "_z_pos"))
        return np.array(x), np.array(y), np.array(z)