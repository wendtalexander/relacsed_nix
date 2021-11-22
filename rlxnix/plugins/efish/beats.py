import nixio
import numpy as np
import matplotlib.pyplot as plt

from .efish_ephys_repro import EfishEphys


class Beats(EfishEphys):
    _repro_name = "Beats"

    def __init__(self, repro_run: nixio.Tag, traces, relacs_nix_version=1.1):
        super().__init__(repro_run, traces, relacs_nix_version=relacs_nix_version)

    @property
    def deltafs(self):
        """ The difference frequencies of the stimuli in Hertz.

        Returns
        -------
        dfs: list of floats
            The difference frequencies of the stimulus presentations in Hertz.
        """
        dfs = [s.metadata[s.name]["DeltaF"][0][0] for s in self.stimuli]
        return dfs

    @property
    def frequencies(self):
        """ The absolute frequencies of the stimuli in Hertz.

        Returns
        -------
        freqs: list of floats
            The absolute frequencies of the stimulus presentations in Hertz.
        """
        freqs = [s.metadata[s.name]["Frequency"][0][0] for s in self.stimuli]
        return freqs

    @property
    def pause(self):
        """The pause between stimuli in seconds.

        Returns
        -------
        p: float
            The pause between stimuli in seconds.
        """
        d = self.metadata["RePro-Info"]["settings"]["pause"][0][0]
        return d

    @property
    def ramp(self):
        """The ramp duration in seconds.

        Returns
        -------
        r: float
            The ramp duration stimuli in seconds.
        """
        r = self.metadata["RePro-Info"]["settings"]["ramp"][0][0]
        return r

    @property
    def eodmult(self):
        """The multiple of EODf.

        Returns
        -------
        m: int
            The multiple of EODf
        """
        m = self.metadata["RePro-Info"]["settings"]["eodmult"][0][0]
        return r

    @property
    def eodmult(self):
        """The multiple of EODf.

        Returns
        -------
        m: int
            The multiple of EODf
        """
        m = self.metadata["RePro-Info"]["settings"]["eodmult"][0][0]
        return m

    @property
    def amplitude(self):
        """The amplitude of the stimuli.

        Returns
        -------
        a: float
            The amplitude.
        unit: str
        """
        a = self.metadata["RePro-Info"]["settings"]["amplitude"][0][0]
        unit = self.metadata["RePro-Info"]["settings"]["amplitude"][1]
        return a, unit
