======
rlxnix
======

Library for reading relacs-flavoured `NIX <https://github.com/g-node/nix>`_ files.

A brief intro
-------------

**relacs** is used to record data and put out stimuli in the context of electrophysiological experiments. It is highly configurable and flexible. What it does is controlled in so-called "**Re**search**Pro**tokols" (RePro). These RePros are organized as **Pluginsets**. Whenever a RePro is active, it will dump continuously sampled and/or event **traces** along with all metadata it knows to file. It may or may not control the stimulation of the recorded system. Usually, the settings of a RePro (the **metadata**) completely define its behavior. In the extreme, however, the stimulus that the RePro puts out changes dynamically depending on the neuronal responses and may vary from trial to trial. Therefor a very flexible storage approach is needed and the generic nature of `NIX <https://github.com/g-node/nix)>`_ data model is well suited for this but, otoh, being generic and flexible make it a little more demanding to read the data.

**rlxnix** simplifies reading of the data from nix files and smooths some edges of generic data storage. In the context of **NIX** we would say that **rlxnix** is a high-level API for reading relacs-flavoured nix files.

Project status and installation
-------------------------------
The **rlxnix** package is in an early state, some things may not work as expected. 

To try it out and install it there are two options:

1) manual installation
2) installation via `TestPyPi <https://test.pypi.org>`__

Manual installation
###################

.. code:: shell

    git clone https://github.com/relacs/relacsed_nix.git
    cd relacsed_nix
    # for installation in "editable" model
    pip install . -e 
    # for normal installation
    pip install .

Installation via test.pypi
##########################

.. code:: shell

    >> pip install -i https://test.pypi.org/simple/ rlxnix

.. toctree::
   :caption: Getting started
   :maxdepth: 1

   introduction

.. toctree::
   :caption: Troubleshooting:
   :maxdepth: 1
   :hidden:

   contact

.. toctree::
   :maxdepth: 1
   :caption: API Reference
   :hidden:

   api/modules

.. toctree::
   :caption: Appendix
   :maxdepth: 1
   :hidden:

   genindex
   py-modindex
   Sources on GitHub <https://github.com/relacs/relacsed_nix>
   License <https://github.com/relacs/relacsed_nix/blob/master/LICENSE.md>
