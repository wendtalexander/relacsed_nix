.. :toctree::
        :maxdepth: 2

Introduction
============

**rlxnix** objects represent the content of a relacs stored NIX file. The file content is modelled as three basic objects (see also figure 1).

1. The *Dataset*: This is the first and most important object that needs to be created by instantiation. It just needs the filename of the recorded file. The Dataset then contains the top-level metadata, i.e. the information that was provided in the file save dialog relacs asks you to fill upon saving a file. The dataset further offers access to the the **Re**search**Pro**tocols that have been run. 
2. *ReProRun*: Represents the run of a single RePro. It has properties such as the start and stop times of the RePro-run. The metadata contain the settings of the RePro. From here you can access the stimuli that have been applied during this run.
3. *Stimulus*: The Stimulus object offers access to the concrete stimulus settings (the metadata) and the data recorded during the stimulus presentations.

.. figure:: ./images/structure.png
   :alt: object structure

   Figure 1: Basic structure of the front-facing objects.



Quickstart
----------

The following code snippet give a quick start to use rlxnix to access a file.

.. code:: python

    import rlxnix as rlx
        
    relacs_nix_file = "data/2021-01-01-aa.nix"
    dataset = rlx.Dataset(relacs_nix_file)
    print(dataset)

    # print out the metadata of the recording session. 
    mdata_dict = dataset.metadata
    print(mdata_dict)

    # print the list of the RePros that have been run in the dataset
    print(dataset.repros)

    # Suppose the dataset contains a BaselineActivity repro run
    baseline = dataset.repro_runs("BaselineActivity-1")[0]  # needs the exact name, returns a list
    print(type(baseline))   # rlxnix.plugins.efish.baseline.Baseline
    print(baseline.metadata)  # prints the metadata dict
    base_spikes = baseline.spikes  # returns the spike times in seconds

    # The SAM repro has been run several times, so far there is no SAM ReProRun class
    sam_runs = dataset.repro_runs("sam", exact=False)
    print(len(sam_runs))  # some number
    sam = sam_runs[0]
    print(type(sam))  # rlxnix.repro.ReProRun  --> This is the generic ReProRun
    print(len(sam.stimuli))  # the number of stimuli run in the ReProRun
    print(sam.stimuli[0].metadata)  # the metadata of the stimulus
    spikes, _  = sam.stimuli[0].trace_data("Spikes-1")  # by default the stimulus start time is subtracted from the spike times
    local_eod_data, time = sam.stimuli[0].trace_data("LocalEOD-1")

    plt.plot(time, local_eod_data)
    plt.scatter(spikes, np.ones_like(spikes) * np.max(local_eod_data), color="tab:red")
    plt.show()