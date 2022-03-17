import os
import nixio
import logging
import numpy as np
from numpy import full
from scipy.interpolate import interp1d

from .efish_ephys_repro import EfishEphys
from ...utils.util import convert_path


class FileStimulus(EfishEphys):
    _repro_name = "FileStimulus"

    def __init__(self, repro_run: nixio.Tag, traces, relacs_nix_version=1.1, stimulus_folder="/data/stimuli"):
        super().__init__(repro_run, traces, relacs_nix_version=relacs_nix_version)
        self._stimulus_folder = stimulus_folder

    @property
    def stimulus_folder(self):
        return self._stimulus_folder

    @stimulus_folder.setter
    def stimulus_folder(self, new_location):
        logging.debug(f"FileStimulus: setting stimulus folder to {new_location}.")
        if os.path.exists(new_location):
            self._stimulus_folder = new_location
        else:
            logging.error(f"FileStimulus: new stimulus folder ({new_location}) does not exist!")

    @property
    def contrast(self):
        # in _mapping_version <= 1.1 this is part of the repro, in future versions the contrast information may move to the features...
        c = 0.0
        unit = ""
        logging.debug("Filestimulus: trying to read contrast from metadata")
        if "RePro-Info" not in self.metadata:
            settings = self.repro_tag.metadata.find_sections(lambda s: s.type == "settings")
            if len(settings) > 0:
                cp = settings[0].props["contrast"]
                if cp.unit is None or len(cp.unit) == 0:
                    c = cp.values[0] * 100
                    unit = "%"
                else:
                    c = cp.values[0]
                    unit = cp.unit
        elif "contrast" in self.metadata["RePro-Info"]["settings"]:
            vals, unit = self.metadata["RePro-Info"]["settings"]["contrast"]
            if len(unit.strip()) == 0:
                c = vals[0] * 100
                unit = "%"
            else:
                c = vals[0]
                unit = unit.strip()
        else:
            logging.error("Filestimulus.contrast: could not find the contrast property!")
        return c, unit

    @property
    def stimulus_filename(self):
        name = None
        logging.debug("Filestimulus: trying to read stimulus file from metadata")
        if "RePro-Info" not in self.metadata:
            settings = self.repro_tag.metadata.find_sections(lambda s: s.type == "settings")
            if len(settings) > 0:
                name = settings[0]["file"]
        elif "file" in self.metadata["RePro-Info"]["settings"]:
            name = self.metadata["RePro-Info"]["settings"]["file"][0][0]
        else:
            logging.error("Filestimulus.stimulus_filename: could not find the stimulus file property!")
        return name

    def _read_stimulus_file(self, filename):
        """
        Loads a data file saved by relacs. Returns a tuple of dictionaries
        containing the data and the header information

        Parameter
        ---------
        filename : str
            Filename of the data file

        Returns
        -------
        tuple
            a tuple of dictionaries containing the head information and the data.
        """
        with open(filename, 'r') as fid:
            L = [l.lstrip().rstrip() for l in fid.readlines()]

        ret = []
        dat = {}
        X = []
        keyon = False
        currkey = None
        for l in L:
            # if empty line and we have data recorded
            if (not l or l.startswith('#')) and len(X) > 0:
                keyon = False
                currkey = None
                dat['data'] = np.array(X)
                ret.append(dat)
                X = []
                dat = {}

            if '---' in l:
                continue
            if l.startswith('#'):
                if ":" in l:
                    tmp = [e.rstrip().lstrip() for e in l[1:].split(':')]
                    if currkey is None:
                        dat[tmp[0]] = tmp[1]
                    else:
                        dat[currkey][tmp[0]] = tmp[1]
                elif "=" in l:
                    tmp = [e.rstrip().lstrip() for e in l[1:].split('=')]
                    if currkey is None:
                        dat[tmp[0]] = tmp[1]
                    else:
                        dat[currkey][tmp[0]] = tmp[1]
                elif l[1:].lower().startswith('key'):
                    dat['key'] = []
                    keyon = True
                elif keyon:
                    dat['key'].append(tuple([e.lstrip().rstrip() for e in l[1:].split()]))
                else:
                    currkey = l[1:].rstrip().lstrip()
                    dat[currkey] = {}

            elif l:  # if l != ''
                keyon = False
                currkey = None
                X.append([float(e) for e in l.split()])

        if len(X) > 0:
            dat['data'] = np.array(X)
        else:
            dat['data'] = []
        ret.append(dat)

        return tuple(ret)


    def load_stimulus(self, stimulus_index=0):
        """Load the stimulus data from the stimulus file. Since the stimulus output might be shorter than the stimulus one needs to provide the stimulus index for automatic adjustments.

        Parameters
        ----------
        stimulus_index : int, optional
            The stimulus index. Defaults to 0

        Returns
        -------
        np.ndarray :
            The stimulus data
        np.ndarray :
            The stimulus time
        """
        self._check_stimulus(stimulus_index=stimulus_index)
        if self._stimulus_folder is None or not os.path.exists(self._stimulus_folder):
            logging.error(f"FileStimulus: Stimulus folder is not set or not accessible! {self._stimulus_folder}")
            return None, None

        stim_name = self.stimulus_filename
        if not stim_name:
            return None, None
        stim_name = convert_path(stim_name)
        stim_file = stim_name.split(os.sep)[-1]

        full_file = os.sep.join([self._stimulus_folder, stim_file])
        if not os.path.exists(full_file) or not os.path.isfile(full_file):
            logging.error(f"FileStimulus: Stimulus file {full_file} does not exist")
            return None, None

        s = self._read_stimulus_file(full_file)
        logging.debug("Filestimulus: successfully parsed stimulus file {full_file}")

        stimulus = self.stimuli[stimulus_index]
        stim_duration = stimulus.duration
        sampling_rate = 1./stimulus.trace_info("V-1").sampling_interval
        inter = interp1d(s[0]['data'][:, 0], s[0]['data'][:, 1])
        time_original = s[0]['data'][:, 0]
        time_resampled = np.linspace(0.0, stim_duration, int(stim_duration * sampling_rate))
        time_resampled[time_resampled > time_original[-1]] = time_original[-1]
        stimulus = inter(time_resampled)

        return stimulus, time_resampled
