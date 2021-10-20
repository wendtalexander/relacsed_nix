from IPython import embed
import matplotlib.pyplot as plt
import rlxnix as rlx

if __name__ == "__main__":
    d = rlx.Dataset("/Volumes/pocketbrain/data/2021-09-03-aa-invivo-2/2021-09-03-aa-invivo-2.nix")
    data = d.repro_data("sam", False)
    sam = data[0]
    data, time = sam.trace_data("V-1")

    embed()