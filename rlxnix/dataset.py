from typing import Optional, Union
import nixio
import os
import pathlib
import inspect
import logging
import weakref
import datetime as dt
from tqdm import tqdm
from importlib import import_module

from .base.stimulus import Stimulus
from .utils.mappings import DataType, type_map
from .base.repro import ReProRun
from .utils.timeline import Timeline
from .utils.util import data_links_to_pandas, nix_metadata_to_dict
from .utils.data_trace import DataTrace, TraceList
from .utils.buffers import MetadataBuffer, FeatureBuffer


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
    def __init__(self, filename: Union[str, pathlib.Path]) -> None:
        super().__init__()
        self._nixfile = None

        if isinstance(filename, str):
            filename = pathlib.Path(filename)

        if not filename.exists:
            logging.error(f"rlxnix cannot read file {filename}, does not exist!")
            raise ValueError(f"RelacsNIX cannot read file {filename}, does not exist!")

        self._filename = filename
        logging.info(f"Dataset: opening nix file {filename}")
        self._nixfile = nixio.File.open(str(filename), nixio.FileMode.ReadOnly)
        weakref.finalize(self._nixfile, self.close)
        self._block = self._nixfile.blocks[0]
        if "relacs-nix version" in self._block.metadata:
            self._relacs_nix_version = self._block.metadata["relacs-nix version"]
            logging.info(f"Relacs nix version is {self._relacs_nix_version}")
        else:
            self._relacs_nix_version = 1.0
        self._baseline_data = []
        self._event_traces = TraceList()
        self._data_traces = TraceList()
        self._trace_map = {}
        self._repro_map = {}
        self._metadata_buffer = MetadataBuffer()
        self._feature_buffer = FeatureBuffer()

        self._scan_file()

    def _scan_stimuli(self):
        for k in tqdm(self._repro_map.keys(), disable=not(logging.root.level == logging.INFO)):
            r = self._repro_map[k]
            stimulus_start = r.start_time
            stimulus_stop = r.start_time + r.duration
            stimulus_names, stimulus_indices, stimulus_starts, stimulus_stops = self._timeline.find_stimuli(stimulus_start, stimulus_stop)
            for name, index, start, stop in zip(stimulus_names, stimulus_indices, stimulus_starts, stimulus_stops):
                if start >= stop:
                    logging.info(f"Dataset: not creating stimulus for stimulus {name} because start time ({start}) is >= stop time ({stop})!")
                    continue
                mt = self._block.multi_tags[name]
                next_stimulus_start = self._timeline.next_stimulus_start(stop)
                s = Stimulus(mt, self._trace_map, index, next_stimulus_start, self._relacs_nix_version)
                r.add_stimulus(s)

    def _scan_repros(self):
        for tag in tqdm(self._block.tags, disable=not(logging.root.level == logging.INFO)):
            if "relacs.repro_run" not in tag.type:
                continue
            if "RePro" in tag.metadata.sections[0]:
                p = tag.metadata.sections[0]["RePro"]
            elif "repro" in tag.metadata.sections[0]:
                p = tag.metadata.sections[0]["repro"]
            else:
                raise KeyError(f"Neither 'repro' nor 'RePro' key found in tag {tag} metadata!")
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
        self._timeline = Timeline(self.name, self._repro_map, self._block.multi_tags, self._relacs_nix_version)
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

    def repro_runs(self, repro_name=None, exact=False) -> list:
        """Returns the RePro class instances providing access to data and metadata of the repro runs.

        Paramters
        ---------
            repro_name : str, optional
                The name of the desired RePro run. If not given, all repro runs are returned. Defaults to None.
            exact : bool, optional
                If True, the name must be an exact match to the actually run RePro runs. If False, all possible matches (case insensitive and repro_name must be part of the name) are returned. Defaults to False.

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

    def find(self, repro_name, **kwargs):
        """Find repro runs according to the repro name, and further settings provided by keyword arguments.

        Parameters
        ----------
        repro_name : str
            The name (fragment) the repro that is passed to self.repro_runs.
        **kwargs :
            Keyword arguments are used to filter repros based on the properties exposed by the respective repro classes.
        """
        repros = self.repro_runs(repro_name)
        if len(repros) == 0:
            print(f"No matching for repro runs for pattern {repro_name}!")

        matches = []
        for r in repros:
            match = True
            for k in kwargs.keys():
                match = match and (hasattr(r, k) and kwargs[k] in getattr(r, k))
            if match:
                matches.append(r)

        return matches

    def find_stimuli(self, repro_name, filter_func=lambda s: True, **kwargs):
        """ Find stimuli that were run in certain repro_runs. The repro runs are selected according to the
        repro_name and the passed keyword arguments (see function find()).
        Additionally, a filter function can be passed that filters the stimuli e.g. on duration.
        
        Parameters:
        -----------
        repro_name: str
            The name (fragment) the repro.
        filter_func: function
            The filter function that is applied to the matching repros.
        **kwargs: dict
            The keyword arguments are used to filter the repro runs.

        Returns:
        --------
        list of stimuli
        """
        repros = self.find(repro_name, **kwargs)
        matches = []
        for r in repros:
            matches.extend([s for s in r if filter_func(s)])

        return matches
        
    def close(self):
        """Close the nix file, if open. Note: Once the file is closed accessing the data via one of the repro run classes will not work!
        """
        if self._nixfile is not None and self._nixfile.is_open():
            self._nixfile.flush()
            self._nixfile.close()
        self._nixfile = None
        self._metadata_buffer.clear(False)
        self._feature_buffer.clear(False)

    @property
    def is_open(self) -> bool:
        """Returns whether the nix file is still open.

        Returns
        -------
        bool
            True if the file is open, False otherwise.
        """
        return self._nixfile is not None and self._nixfile.is_open()

    @property
    def name(self) -> str:
        """Returns the name of the dataset (i.e. the full filename)
        
        Returns
        -------
        str
            The full filename
        """
        return str(self._filename.resolve())

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
    def recording_date(self) -> Optional[str]:
        """The recording data of the dataset

        Returns
        -------
        Optional[str]
            iso-format string of the file creation timestamp
        """
        date = None
        if not self.is_open or not self._nixfile:
            return None

        if self.is_open:
            if self._nixfile:
                date = str(dt.datetime.fromtimestamp(self._nixfile.created_at))
                return date

    def data_links(self, include_repros=True):
        """Returns a list of DataLink objects for reproRun and StimulusSegment entities in the dataset.

        Parameters
        ----------
        include_repros : bool, optional
            Whether or not to include the ReProRuns, by default True

        Returns
        -------
        list of DataLink 
            DataLink objects.
        """
        dls = []
        for r in self.repro_runs():
            if include_repros:
                dls.append(r.data_link)
            dls.extend(r.stimulus_data_links)
        return dls

    def to_pandas(self, include_repros=True):
        """Exports the DataLinks to all data segments stored in the dataset to a pandas DataFrame

        Parameters
        ----------
        include_repros : bool, optional
            Whether or not to include the ReProRuns, by default True

        Returns
        -------
        pandas.DataFrame
            The data frame
        """
        dls = self.data_links(include_repros)
        return data_links_to_pandas(dls)

    @property
    def metadata(self) -> dict:
        """Get the Metadata associated with this recording. Dict entries are the respective property name as key and value is a tuple of the property's values and the unit if provided.

        Returns
        -------
        dictionary
            The session metadata.
        """
        mdata = nix_metadata_to_dict(self._block.metadata)
        return mdata

    def plot_timeline(self) -> None:
        self._timeline.plot()

    def __contains__(self, key):
        if isinstance(key, int):
            return key < len(self._repro_map.keys())
        elif isinstance(key, str):
            return key in self.repros
        raise KeyError(f"Invalid key! Key {key} is not str or int.")

    def __getitem__(self, key):
        if not key in self:
            raise KeyError(f"Key {key} not found in list of repro runs!")
        if isinstance(key, str):
            return self.repro_runs(key, exact=True)[0]
        else:
            return self.repro_runs()[key]

    def __str__(self) -> str:
        info = "{n:s}\n\tlocation: {l:s}\n\trecording data: {rd:s}\n\tfile size {s:.2f} MB"
        return info.format(**{"n": self.name.split(os.sep)[-1],
                              "l": os.sep.join(self.name.split(os.sep)[:-1]),
                              "rd": self.recording_date,
                              "s":  self._filename.stat().st_size / 1e+6})

    def __repr__(self) -> str:
        repr = "Dataset object for file {name:s} at {id}"
        return repr.format(name=self.name, id=hex(id(self)))
