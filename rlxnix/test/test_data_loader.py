import os
import nixio
import logging
import rlxnix as rlx
from rlxnix.utils.data_loader import SegmentType


def test_to_pandas():
    filename = os.path.join("..", "..", "data", "2021-11-11-aa.nix")
    if not os.path.exists(filename):
        logging.warning(f"file {filename} not found! Skipping test 'test_data_loader.test_to_pandas'")
        return
    dataset  = rlx.Dataset(filename)
    repro_count = 0
    stimulus_count = 0
    for r in dataset.repro_runs():
        repro_count += 1
        stimulus_count += len(r.stimuli)

    df = dataset.to_pandas()
    assert len(df) == repro_count + stimulus_count
    assert len(df[df.segment_type == str(SegmentType.ReproRun)] == repro_count)
    assert len(df[df.segment_type == str(SegmentType.StimulusSegment)] == stimulus_count)


def test_from_pandas():
    filename = os.path.join("..", "..", "data", "2021-11-11-aa.nix")
    dataset  = rlx.Dataset(filename)
    if not os.path.exists(filename):
        logging.warning(f"file {filename} not found! Skipping test 'test_data_loader.test_to_pandas'")
        return
    df = dataset.to_pandas()
    assert len(df) > 0
    dl = rlx.from_pandas(df, 100)
    assert dl is None
    dl = rlx.from_pandas(df, 10)
    assert dl is not None
    assert dl.tag_id == df["tag_id"].values[10]
    
    dls = rlx.from_pandas(df, segment_type=SegmentType.ReproRun)
    assert isinstance(dls, list)
    for dl in dls:
        assert dl.segment_type == str(SegmentType.ReproRun)
    
    dls = rlx.from_pandas(df, segment_type=SegmentType.StimulusSegment)
    assert isinstance(dls, list)
    for dl in dls:
        assert dl.segment_type == str(SegmentType.StimulusSegment)