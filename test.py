from IPython import embed
import matplotlib.pyplot as plt
import rlxnix as rlx
import platform

if __name__ == "__main__":
    if "macos" in platform.platform().lower():
        d = rlx.Dataset("/Volumes/pocketbrain/data/2021-09-03-aa-invivo-2/2021-09-03-aa-invivo-2.nix")
    else:
        d = rlx.Dataset("/media/grewe/pocketbrain/data/2021-09-03-aa-invivo-2/2021-09-03-aa-invivo-2.nix")
    
    data = d.repro_data("sam", False)
    baseline_data = d.repro_data("baseline", False)[0]
    sam = data[0]
    data, time = sam.trace_data("V-1")
    bd, bt = baseline_data.trace_data("V-1")
    spike_times, _ = baseline_data.trace_data("Spikes-1")
    plt.plot(bt, bd)
    plt.scatter(spike_times, np.ones_like(spike_times) * np.max(bd))
    plt.show()
    embed()