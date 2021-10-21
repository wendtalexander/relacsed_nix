import numpy as np
import nixio

from IPython import embed


class Stimulus(object):

    def __init__(self, stimulus_mtag: nixio.MultiTag, index: int) -> None:
        super().__init__()
        self._mtag = stimulus_mtag
        self._index = index

    @property
    def start_time(self):
        return self._mtag.positions[self._index, 0][0]

    @property
    def duration(self):
        return self._mtag.extents[self._index, 0][0] if self._mtag.extents else 0.0

    @property
    def references(self) -> list:
        """The list of referenced event and data traces

        Returns:
            List: index, name and type of the references
        """
        refs = []
        for i, r in enumerate(self._mtag.references):
            refs.append((i, r.name, r.type))
        return refs

    @property
    def features(self) -> list:
        """List of features associated with this repro run.

        Returns:
            List: name and type of t[description]
        """
        features = []
        for i, feats in enumerate(self._mtag.features):
            features.append((i, feats.data.name, feats.data.type))
        return features

    def trace_data(self, name_or_index):
        """Get the data that was recorded while this repro was run.

        Args:
            name_or_index (str or int): name or index of the referenced data trace

        Returns:
            data (numpy array): the data 
            time (numpy array): the respective time vector, None, if the data is an event trace
        """
        ref = self._mtag.references[name_or_index]
        time = None
        data = ref.get_slice([self.start_time], [self.duration], nixio.DataSliceMode.Data)[:]
        if "relacs.data.sampled" in ref.type:
            time = np.array(ref.dimensions[0].axis(len(data), start_position=self.start_time))
        return data, time
    
    def feature_data(self, name_or_index):
        feat_data = self._mtag.feature_data(name_or_index, self._index)
        return feat_data[:]

    def __str__(self) -> str:
        name = self._mtag.name
        tag_type = self._mtag.type
        info = "Stimulus: {n:s} \t type: {t:s}\n\tstart time: {st:.2f}s, duration: {dur:.2f}s"
        return info.format(n=name, t=tag_type, st=self.start_time, dur=self.duration)

    def __repr__(self) -> str:
        return super().__repr__()