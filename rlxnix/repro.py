from IPython.terminal.embed import embed
import nixio
import numpy as np

from rlxnix.stimulus import Stimulus


class ReProRun(object):
    """This class represents the data of a RePro run. It offers access to the data and metadata.
    """

    def __init__(self, repro_run: nixio.Tag, relacs_nix_version=1.1):
        """Create a RePro instance that represent one run of a relacs RePro.

        Args:
            repro_run (nixio.Tag): the nix - tag that belong to the repro run 
            relacs_nix_version (float, optional): The mapping version number. Defaults to 1.1.
        """
        super().__init__()
        self._repro_run = repro_run
        self._relacs_nix_version = relacs_nix_version
        self._start_time = repro_run.position[0]
        self._duration = repro_run.extent[0]
        self._stimuli = []

    @property
    def name(self) -> str:
        """The name of the repro run

        Returns:
            string: the name
        """
        return self._repro_run.name

    @property
    def type(self) -> str:
        """The type of the repro run

        Returns:
            string: the type
        """
        return self._repro_run.type

    @property
    def start_time(self) -> float:
        """The start time of the 

        Returns:
            float: RePro start time
        """
        return self._start_time

    @property
    def duration(self) -> float:
        """The duration of the repro run in seconds.

        Returns:
            float: the duration in seconds.
        """
        return self._duration

    @property
    def repro_tag(self) -> nixio.Tag:
        """[summary]

        Returns:
            [type]: [description]
        """
        return self._repro_run

    @property
    def references(self) -> list:
        """The list of referenced event and data traces

        Returns:
            List: index, name and type of the references
        """
        refs = []
        for i, r in enumerate(self._repro_run.references):
            refs.append((i, r.name, r.type))
        return refs

    @property
    def features(self) -> list:
        """List of features associated with this repro run.

        Returns:
            List: name and type of t[description]
        """
        features = []
        for i, feats in enumerate(self._repro_run.features):
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
        ref = self._repro_run.references[name_or_index]
        time = None
        data = ref.get_slice([self.start_time], [self.duration], nixio.DataSliceMode.Data)[:]
        if "relacs.data.sampled" in ref.type:
            time = np.array(ref.dimensions[0].axis(len(data), start_position=self.start_time))
        return data, time

    def feature_data(self, name_or_index):
        feat_data = self._repro_run.feature_data(name_or_index)
        return feat_data[:]
    
    @property
    def metadata(self):
        m = util.nix_metadata_to_dict(self._repro_run.metadata)
        return m

    def add_stimulus(self, stimulus:Stimulus):
        self._stimuli.append(stimulus)

    @property
    def stimuli(self):
        return self._stimuli

    def __str__(self) -> str:
        info = "Repro: {n:s} \t type: {t:s}\n\tstart time: {st:.2f}s\tduration: {et:.2f}s"
        return info.format(n=self.name, t=self.type, st=self.start_time, et=self.duration)

    def __repr__(self) -> str:
        return super().__repr__()