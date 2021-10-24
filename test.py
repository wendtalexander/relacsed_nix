from IPython import embed
import matplotlib.pyplot as plt
import rlxnix as rlx
import platform
import numpy as np
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
  
    if "macos" in platform.platform().lower():
        # d = rlx.Dataset("/Volumes/pocketbrain/data/2021-09-03-aa-invivo-2/2021-09-03-aa-invivo-2.nix")
        d = rlx.Dataset("data/2021-07-08-ad-invivo-1.nix")
    else:
        d = rlx.Dataset("/media/grewe/pocketbrain/data/2021-09-03-bv-invivo-2/2021-09-03-bv-invivo-2.nix")

    embed()
    exit()
    sam_runs = d.repro_runs("sam", False)
    baseline_data = d.repro_runs("baseline", False)[0]
    
    sam = sam_runs[0]
    sam_stim0 = sam.stimuli[0]
    data, time = sam_stim0.trace_data("LocalEOD-1")
    sam_spikes, _ = sam_stim0.trace_data("Spikes-1")
    
    plt.plot(time, data)
    plt.scatter(sam_spikes, np.ones_like(sam_spikes)*np.max(data), color="tab:red")


    bd, bt = baseline_data.trace_data("V-1")
    spike_times, _ = baseline_data.trace_data("Spikes-1")
    plt.plot(bt, bd)
    plt.scatter(spike_times, np.ones_like(spike_times) * np.max(bd))
    plt.show()
    embed()