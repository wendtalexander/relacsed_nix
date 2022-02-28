# rlxnix - relacsed nix

Library for reading relacs-flavoured [NIX](https://github.com/g-node/nix) files.

## A brief intro

**relacs** is used to record data and put out stimuli in the context of electrophysiological experiments. It is highly configurable and flexible. What it does is controlled in so-called "**Re**search**Pro**tokols" (RePro). These RePros are organized as **Pluginsets**. Whenever a RePro is active, it will dump continuously sampled and/or event **traces** along with all metadata it knows to file. It may or may not control the stimulation of the recorded system. Usually, the settings of a RePro (the **metadata**) completely define its behavior. In the extreme, however, the stimulus that the RePro puts out changes dynamically depending on the neuronal responses and may vary from trial to trial. Therefor a very flexible storage approach is needed and the generic nature of [NIX](https://github.com/g-node/nix) data model is well suited for this but, otoh, being generic and flexibility make it a little more demanding to read the data.

**rlxnix** simplifies the reading of the data from nix files and smooths some edges of the generic storage. IN the context of [NIX](https://github.com/g-node/nix) we would say that **rlxnix** is a high-level API for reading relacs-flavoured nix files.

## Using **rlxnix** starter

```python
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
```

## Adding new RePro classes

**relacs** plugins implement/inherit the RePro interface. Here we follow a similar approach and **rlxnix** has a plugin sub-package that in turn contains plugin sets (e.g. efish) which contains several classes that each represent and offer some convenience for accessing the data recorded during the run of a specific RePro, e.g. the *Baseline* repro.

These classes inherit from rlxnix.ReProRun. If you write your own repro class it has to inherit from **ReProRun** and must have a class member ``_repro_name`` that matches the name of the **relacss** repro it represents. It must further be added to the import statement(s) in the \__init.py\__ (e.g.: rlxnix/plugins/efish/\__init.py\__). If you add your own pluginset this has to be added to the plugins/\__init.py\__ file. Otherwise the classes will not be automatically detected.


## Installation

The easiest way is to install it via pip using the test/pypi package

```pip install -i https://test.pypi.org/simple/ rlxnix```
