import nixio

from .trace_container import TraceContainer


class Stimulus(TraceContainer):
    """[summary]

    Args:
        TraceContainer ([type]): [description]
    """
    def __init__(self, stimulus_mtag: nixio.MultiTag, index: int, relacs_nix_version=1.1) -> None:
        super().__init__(stimulus_mtag, index, relacs_nix_version=relacs_nix_version)
        self._mtag = stimulus_mtag

    def __str__(self) -> str:
        name = self._mtag.name
        tag_type = self._mtag.type
        info = "Stimulus: {n:s} \t type: {t:s}\n\tstart time: {st:.2f}s, duration: {dur:.2f}s"
        return info.format(n=name, t=tag_type, st=self.start_time, dur=self.duration)

    def __repr__(self) -> str:
        return super().__repr__()