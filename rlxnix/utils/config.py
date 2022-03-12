import os
import logging
import json
from enum import Enum, auto
from IPython import embed

from .buffers import Singleton


class Configuration(Enum):
    Default = auto()
    Local = auto()
    Automatic = auto()


class Config(metaclass=Singleton):
    """
    
    
    """
    trace_configuration_name = "trace_configs"
    log_level_name = "log_level"

    def __init__(self) -> None:
        super().__init__()
        logging.debug("Init Config!")
        self._default_config = {}
        self._local_config = {}
        self._read_default_config()
        self._read_local_config()

    def _read_default_config(self):
        logging.debug("Config: default configurations")
        here = os.path.dirname(__file__)
        config_file_name = os.path.join(here, "default_config.json")
        if not os.path.exists(config_file_name):
            logging.warning(f"rlxnix.Config: no default configuration found! {config_file_name}")
            return

        with open(os.path.join(here, "default_config.json")) as config_file:
            infodict = json.load(config_file)
        self._default_config = infodict

    def _read_local_config(self):
        logging.debug("Config: Read local configurations!")
        local = os.getcwd()
        config_file_name = os.path.join(local, "config.json")
        if os.path.exists(config_file_name):
            with open(config_file_name) as config_file:
                local_config = json.load(config_file)
            self._local_config = local_config
        else:
            logging.info(f"rlxnix.Config: no local configuration found! {config_file_name}")

    def _get_trace_config(self, config_dict, plugin, signal=None):
        if self.trace_configuration_name in config_dict.keys():
            c_dict = config_dict[self.trace_configuration_name]
            if plugin in c_dict:
                logging.debug(f"Config found key {plugin} in config {plugin in c_dict}!")
                cfg = c_dict.get(plugin, None)
                if cfg is not None:
                    if signal is not None:
                        if signal in cfg.keys():
                            return cfg[signal]
                        else:
                            return None
                    else:
                        return cfg
        return None

    def trace_configuration(self, plugin, signal=None):
        """[summary]

        Parameters
        ----------
        plugin : [type]
            [description]
        signal : [type], optional
            [description], by default None

        Returns
        -------
        [type]
            [description]
        """
        cfg = self._get_trace_config(self._local_config, plugin, signal)
        if cfg is not None:
            return cfg
        return self._get_trace_config(self._default_config, plugin, signal)

    def _get_log_level(self, configuration):
        if self.log_level_name in configuration:
            return configuration[self.log_level_name]
        else:
            return None

    def log_level(self, config_type=Configuration.Automatic):
        ll = None
        if config_type == Configuration.Local or config_type == Configuration.Automatic:
            ll = self._get_log_level(self._local_config)
        if ll is None and (config_type == Configuration.Automatic or config_type == Configuration.Default):
            ll = self._get_log_level(self._default_config)
        return ll
