.. 2dmat documentation master file, created by
   sphinx-quickstart on Tue May 26 18:44:52 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tutorials
================================

``2DMAT-LEED`` provides a direct problem solver for 2DMAT that uses ``SATLEED`` developed by M. A. Van Hove for the analyses of the low-energy electron diffraction (LEED) data.
``SATLEED`` calculates diffraction data for given atomic positions.
Regarding this as a direct problem, it corresponds to an inverse problem to find optimal atomic coordinates that reproduce the diffraction data obtained from the experiment.
2DMAT provides a framework to solve these inverse problems.

In this tutorial, we will instruct how to use 2DMAT-LEED to find optimal configuration by the grid search (mapper).
We use ``py2dmat-leed`` program included in 2DMAT-LEED with input files in TOML format.
Next, we will explain how to write your own main program for analyses.


.. toctree::
   :maxdepth: 1

   mapper
   user_program
