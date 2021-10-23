from ...repro import ReProRun

class ReceptiveField(ReProRun):
    _repro_name = "ReceptiveField"
    
    def __init__(self, repro_run, relacs_nix_version=1.1) -> None:
        super().__init__(repro_run, relacs_nix_version)
        
