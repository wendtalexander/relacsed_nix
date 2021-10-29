from IPython import embed
import matplotlib.pyplot as plt
import rlxnix as rlx
import platform
import numpy as np
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
  
    if "macos" in platform.platform().lower():
        # d = rlx.Dataset("/Volumes/pocketbrain/data/2021-09-03-aa-invivo-2/2021-09-03-aa-invivo-2.nix")
        d = rlx.Dataset("data/2021-07-08-ad-invivo-1.nix")
    else:
        #d = rlx.Dataset("/media/grewe/pocketbrain/data/2021-09-03-bv-invivo-2/2021-09-03-bv-invivo-2.nix")
        d = rlx.Dataset("/data/invivo/2021-08-03-ab-invivo-1/2021-08-03-ab-invivo-1.nix")
    sam_runs = d.repro_runs("sam", False)
    if len(sam_runs) > 0: 
        sam = sam_runs[0]
        sam_stim0 = sam.stimuli[0]
        print(sam_stim0.id)
        print(sam_stim0.repro_tag_id)
        data, time = sam_stim0.trace_data("LocalEOD-1")
        sam_spikes, _ = sam_stim0.trace_data("Spikes-1")
        
        plt.plot(time, data)
        plt.scatter(sam_spikes, np.ones_like(sam_spikes)*np.max(data), color="tab:red")

    baseline_data = d.repro_runs("baseline", False)
    if len(baseline_data) > 0:
        bd, bt = baseline_data[0].trace_data("V-1")
        spike_times, _ = baseline_data[0].trace_data("Spikes-1")
        plt.plot(bt, bd)
        plt.scatter(spike_times, np.ones_like(spike_times) * np.max(bd))
    plt.close()


    chirps = d.repro_runs("Eigen", exact=False)
    if len(chirps) > 0:
        chirp = chirps[0]
        chirp.plot_overview()

    filestims = d.repro_runs("filestim", exact=False)
    if len(filestims) > 0:
        f = filestims[0]
        v1, vt = f.membrane_voltage(0)
        stim, time = f.load_stimulus() 
    d._timeline.plot()
    embed()