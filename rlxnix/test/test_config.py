import rlxnix as r
import logging

from ..utils.config import Configuration

def test_config_singleton():
    cfg = r.Config()
    assert id(cfg) == id(r._config)

def test_trace_config():
    assert r._config._default_config is not None
    assert r._config.trace_configuration("efish") is not None and isinstance(r._config.trace_configuration("efish"), dict)
    assert isinstance(r._config.trace_configuration("efish", "spikes"), list)
    assert r._config.trace_configuration("unknown") is None
    assert isinstance(r._config.trace_configuration("default", "membrane voltage"), list)

def test_log_level():
    assert r._config.log_level(Configuration.Default) == logging.getLevelName(logging.WARN)
    assert r._config.log_level(Configuration.Automatic) == logging.getLevelName(logging.DEBUG)
    assert r._config.log_level(Configuration.Local) == logging.getLevelName(logging.DEBUG)

