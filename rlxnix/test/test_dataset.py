import os
import nixio
import logging
import rlxnix as rlx
from rlxnix.utils.data_loader import SegmentType


def test_log_level():
    levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]

    for l in levels:
        rlx.set_log_level(l)
        logger = logging.getLogger()
        assert logging.getLevelName(logger.level) == l


def test_open_close():
    filename = os.path.join("..", "..", "data", "2021-11-11-aa.nix")
    if not os.path.exists(filename):
        logging.warning(f"file {filename} not found! Skipping test 'test_dataset.test_open'")
        return
    dataset  = rlx.Dataset(filename)

    assert dataset.is_open == True
    assert dataset._nixfile.is_open()
    assert dataset.name == filename
    assert "2021-11-11" in dataset.recording_date

    dataset.close()
    assert dataset.nix_file == None


def test_stimuli():
    filename = os.path.join("..", "..", "data", "2021-11-11-aa.nix")
    if not os.path.exists(filename):
        logging.warning(f"file {filename} not found! Skipping test 'test_dataset.test_open'")
        return

    dataset  = rlx.Dataset(filename)
    stimulus_count = 0
    for r in dataset.repro_runs():
        stimulus_count += len(r.stimuli)
    assert stimulus_count == sum([len(mt.positions) for mt in dataset._block.multi_tags if "stimulus" in mt.type and "init" not in mt.name])


def test_repros():
    filename = os.path.join("..", "..", "data", "2021-11-11-aa.nix")
    if not os.path.exists(filename):
        logging.warning(f"file {filename} not found! Skipping test 'test_dataset.test_open'")
        return

    dataset  = rlx.Dataset(filename)

    assert len(dataset.repro_runs()) == len([t for t in dataset._block.tags if "repro" in t.type])
    names = [t.name for t in dataset._block.tags if "repro" in t.type]
    for name in names:
        assert name in dataset.repros
