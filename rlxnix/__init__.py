import logging
from .dataset import Dataset
from .base.trace_container import TimeReference
from .utils.timeline import IntervalMode
from .utils.util import data_links_to_pandas
from .utils.data_loader import load_data_segment, from_pandas
from .utils.config import Config
from .info import VERSION, AUTHOR

_config = Config()
logging.basicConfig(level=logging._nameToLevel[_config.log_level()], force=True)

__version__ = VERSION
__author__ = AUTHOR
__all__ = ["Dataset", "TimeReference", "IntervalMode", 
           "data_links_to_pandas", "from_pandas", "load_data_segment",
           "_config"]


def set_log_level(level_name):
    """Set the log level manually.

    Parameters
    ----------
    level_name : str
        The desired log level. Options are ``CRITICAL``, ``ERROR``, ``WARNING``, ``INFO``, and ``DEBUG``.
    """
    logging.basicConfig(level=logging._nameToLevel[level_name], force=True)