import nixio as nix
import os
import inspect
from importlib import import_module
import datetime as dt

from rlxnix.mappings import type_map
from rlxnix.repro import RePro

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
            subm = import_module(f"rlxnix.plugins.{d}.{mc}")
            members = inspect.getmembers(subm, inspect.isclass)
            for _, member in members:
                if hasattr(member, "_repro_name"):
                    repro_name = getattr(member, "_repro_name")
                    if repro_name not in repro_map.keys():
                        repro_map[repro_name] = member
    return repro_map


repro_class_map = scan_plugins()


class Dataset(object):

    def __init__(self, filename) -> None:
        super().__init__()
        if not os.path.exists(filename):
            raise ValueError("RelacsNIX cannot read file %s, does not exist!" %filename)
        self._filename = filename
        self._nixfile = nix.File.open(filename, nix.FileMode.ReadOnly)
        self._block = self._nixfile.blocks[0]
        if "relacs-nix version" in self._block.metadata:
            self._relacs_nix_version = self._block.metadata["relacs-nix version"]
        else:
            self._relacs_nix_version = 1.0
        self._baseline_data = []
        self._repro_runs = []
        self._event_traces = []
        self._data_traces = []
        self._repro_map = {}
        self._scan_file()

    def _scan_repros(self):
        for tag in self._block.tags:
            if "relacs.repro_run" not in tag.type:
                continue
            p = tag.metadata.sections[0]["RePro"]
            if isinstance(p, bytes):
                repro_name = p.decode()
            else:
                repro_name = str(p)
            if repro_name in repro_class_map.keys():
                self._repro_map[tag.name] = repro_class_map[repro_name](tag, self._relacs_nix_version)
            else:
                self._repro_map[tag.name] = RePro(tag, self._relacs_nix_version)

    def _scan_traces(self):
        self._event_traces = [da.name for da in self._block.data_arrays if type_map[self._relacs_nix_version]["event trace"] in da.type]
        self._data_traces = [da.name for da in self._block.data_arrays if type_map[self._relacs_nix_version]["data trace"] in da.type]

    def _scan_file(self):
        self._scan_repros()
        self._scan_traces()

    @property
    def repros(self):
        return list(self._repro_map.keys())
    
    @property
    def event_trace_names(self):
        return self._event_traces

    @property
    def data_trace_names(self):
        return self._data_traces
    
    def repro_data(self, repro_name, exact=True):
        if exact:
            if repro_name in self._repro_map.keys():
                return self._repro_map[repro_name]
        else:
            return [self._repro_map[k] for k in self._repro_map.keys() if repro_name.lower() in k.lower()]

    def close(self):
        if self._nixfile.is_open():
            self._nixfile.close()
        self._nixfile = None

    @property
    def is_open(self):
        return self._nixfile and self._nixfile.is_open()

    @property
    def name(self):
        return self._filename

    @property
    def nix_file(self):
        return self._nixfile if self.is_open else None

    @property
    def recording_date(self):
        return self._nixfile.created_at if self.is_open else None
        date = None
        if self.is_open:
            date = str(dt.datetime.fromtimestamp(self._nixfile.created_at))
        return date

    def __str__(self) -> str:
        return "%s" % self._filename
    
    def __repr__(self) -> str:
        return super().__repr__()

    def __del__(self):
        """make sure, the nix-file is closed.
        """
        if self.is_open:
            self.close()
