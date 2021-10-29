import nixio
import os
import inspect
import logging
import datetime as dt
from tqdm import tqdm
from importlib import import_module

from .stimulus import Stimulus
from .mappings import DataType, type_map
from .repro import ReProRun
from .timeline import Timeline
from .util import nix_metadata_to_dict
from .data_trace import DataTrace

from IPython import embed


def scan_plugins():
    repro_map = {}
    import rlxnix.plugins
    for d in dir(rlxnix.plugins):
        if "__" in d or "rlxnix" in d:
            continue
        m = import_module(f"rlxnix.plugins.{d}")
        for mc in dir(m):
            if "__" in mc or "rlxnix" in d:
                continue
            submodule = import_module(f"rlxnix.plugins.{d}.{mc}")
            members = inspect.getmembers(submodule, inspect.isclass)
            for _, member in members:
                if hasattr(member, "_repro_name"):
                    repro_name = getattr(member, "_repro_name")
                    if repro_name not in repro_map.keys():
                        repro_map[repro_name] = member
    return repro_map


repro_class_map = scan_plugins()


class Dataset(object):
    """Class that represents the content of a single NIX file. All access works file attached, that is, the nix file is kept open as long as Dataset instance exists or until it was explicitely closed. 
    Once the file is closed all access to the data will no longer be possible.

    .. code-block:: python
    
        import rlxnix as rlx
        
        relacs_nix_file = "data/2021-01-01-aa.nix"
        dataset = rlx.Dataset(relacs_nix_file)
        print(dataset)

        for r in dataset.repros:
        print(r)
    """
    def __init__(self, filename) -> None:
        super().__init__()
        if not os.path.exists(filename):
            logging.error("rlxnix cannot read file %s, does not exist!" % filename)
            raise ValueError("RelacsNIX cannot read file %s, does not exist!" % filename)
        logging.info(f"Dataset: opening nix file {filename}")
        self._filename = filename
        self._nixfile = nixio.File.open(filename, nixio.FileMode.ReadOnly)
        self._block = self._nixfile.blocks[0]
        if "relacs-nix version" in self._block.metadata:
            self._relacs_nix_version = self._block.metadata["relacs-nix version"]
            logging.info(f"Relacs nix version is {self._relacs_nix_version}")
        else:
            self._relacs_nix_version = 1.0
        self._baseline_data = []
        self._repro_runs = []
        self._event_traces = []
        self._data_traces = []
        self._trace_map = {}
        self._repro_map = {}
        self._scan_file()

    def _scan_stimuli(self):
        for k in tqdm(self._repro_map.keys(), disable=not(logging.root.level == logging.INFO)):
            r = self._repro_map[k]
            stimulus_start = r.start_time
            stimulus_stop = r.start_time + r.duration
            stimulus_names, stimulus_indices, _, stimulus_stops = self._timeline.find_stimuli(stimulus_start, stimulus_stop)
            for name, index, stop in zip(stimulus_names, stimulus_indices, stimulus_stops):
                mt = self._block.multi_tags[name]
                next_stimulus_start = self._timeline.next_stimulus_start(stop)
                s = Stimulus(mt, self._trace_map, index, next_stimulus_start, self._relacs_nix_version)
                r.add_stimulus(s)

    def _scan_repros(self):
        for tag in tqdm(self._block.tags, disable=not(logging.root.level == logging.INFO)):
            if "relacs.repro_run" not in tag.type:
                continue
            p = tag.metadata.sections[0]["RePro"]
            if isinstance(p, bytes):
                repro_name = p.decode()
            else:
                repro_name = str(p)
            if repro_name in repro_class_map.keys():
                self._repro_map[tag.name] = repro_class_map[repro_name](tag, self._trace_map, self._relacs_nix_version)
            else:
                self._repro_map[tag.name] = ReProRun(tag, self._trace_map, 
                                                     self._relacs_nix_version)

    def _scan_traces(self):
        event_type = type_map[self._relacs_nix_version][DataType.Event]
        continuous_type = type_map[self._relacs_nix_version][DataType.Continuous]

        for da in self._block.data_arrays:
            if event_type in da.type:
                self._event_traces.append(DataTrace(da, self._relacs_nix_version))
                self._trace_map[self.event_traces[-1].name] = self._event_traces[-1]
            elif continuous_type in da.type:
                self._data_traces.append(DataTrace(da, self._relacs_nix_version))
                self._trace_map[self.data_traces[-1].name] = self._data_traces[-1]
            else:
                continue

    def _scan_file(self):
        logging.info(f"Scanning file {self.name}")
        self._scan_traces()
        logging.info("Searching repro runs...")
        self._scan_repros()
        logging.info(f"Creating timeline ...")
        self._timeline = Timeline(self.name, self._repro_map, self._block.multi_tags)
        logging.info("Sorting stimuli...")
        self._scan_stimuli()
        logging.info("...done")

    @property
    def repros(self) -> list:
        """Returns the RePros that have been run in this dataset

        Returns
        -------
        list
            The RePro names.
        """
        return list(self._repro_map.keys())

    @property
    def event_traces(self) -> list:
        """Returns the names of the recorded event traces such as the detected spikes or other events.

        Returns
        -------
        list
            the trace rlxnix.DataTrace instances.
        """
        return self._event_traces

    @property
    def data_traces(self) -> list:
        """Returns the names of the recorded data traces such as the membrane potential.

        Returns
        -------
            list: the rlxnix.DataTrace instances.
        """
        return self._data_traces

    def repro_runs(self, repro_name=None, exact=True) -> list:
        """Returns the RePro class instances providing access to data and metadata of the repro runs.

        Paramters
        ---------
            repro_name : str, optional
                The name of the desired RePro run. If not given, all repro runs are returned. Defaults to None.
            exact : bool, optional
                If True, the name must be an exact match to the actually run RePro runs. If False, all possible matches are returned. Defaults to True.

        Returns
        -------
        list 
            List of RePro class instances that match the repro_name. If repro_name is not given, all repro runs are returned. May be empty.
        """
        def not_found_error(name, exact):
            logging.warning(f"No repro run with the name {name} found with exact={exact}")

        matches = []
        if not repro_name:
            matches = [self._repro_map[k] for k in self._repro_map.keys()]
        else:
            if exact:
                if repro_name in self._repro_map.keys():
                    matches = [self._repro_map[repro_name]]
                else:
                    not_found_error(repro_name, exact)
            else:
                matches = [self._repro_map[k] for k in self._repro_map.keys() if repro_name.lower() in k.lower()]
                if len(matches) < 1:
                    not_found_error(repro_name, exact)
        return matches

    def close(self):
        """Close the nix file, if open. Note: Once the file is closed accessing the data via one of the repro run classes will not work!
        """
        if self._nixfile.is_open():
            self._nixfile.close()
        self._nixfile = None

    @property
    def is_open(self) -> bool:
        """Returns whether the nix file is still open.

        Returns
        -------
        bool
            True if the file is open, False otherwise.
        """
        return self._nixfile and self._nixfile.is_open()

    @property
    def name(self) -> str:
        """Returns the name of the dataset (i.e. the full filename)
        
        Returns
        -------
        str
            The full filename
        """
        return self._filename

    @property
    def nix_file(self) -> nixio.File:
        """Returns the nix-file.

        Returns
        -------
        nixio.File
            The nix file, if open, None otherwise.
        """
        return self._nixfile if self.is_open else None

    @property
    def recording_date(self) -> str:
        """The recording data of the dataset

        Returns
        -------
        str
            iso-format string of the file creation timestamp
        """
        date = None
        if self.is_open:
            date = str(dt.datetime.fromtimestamp(self._nixfile.created_at))
        return date

    @property
    def metadata(self):
        """Get the Metadata associated with this recording. Dict entries are the respective property name as key and value is a tuple of the property's values and the unit if provided.

        Returns
        -------
        dictionary
            The session metadata.
        """
        mdata = nix_metadata_to_dict(self._block.metadata)
        return mdata

    @property
    def plot_timeline(self):
        self._timeline.plot()

    def __str__(self) -> str:
        info = "{n:s}\n\tlocation: {l:s}\n\trecording data: {rd:s}\n\tfile size {s:.2f} MB"
        return info.format(**{"n": self.name.split(os.sep)[-1],
                              "l": os.sep.join(self.name.split(os.sep)[:-1]),
                              "rd": self.recording_date,
                              "s": os.path.getsize(self._filename)/1e+6})

    def __repr__(self) -> str:
        return super().__repr__()

    def __del__(self):
        """make sure, the nix-file is closed.
        """
        if self.is_open:
            self.close()
