.. 2dmat documentation master file, created by
   sphinx-quickstart on Tue May 26 18:44:52 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tutorials
================================

The direct problem solver, ``sim_trhepd_rheed``, is based on the Reflection-High-Energy Electron Diffraction (RHEED, TRHEPD) analysis software developed by Prof. Takashi Hanada at Tohoku University.

In TRHEPD, when atomic coordinates are given, diffraction data is given as a simulation result. 
Therefore, we are dealing with the direct problem from atomic coordinates to diffraction data.
On the other hand, in many cases, diffraction data is given experimentally, and the atomic coordinates are required to reproduce the experimental data. These are inverse problems to the above direct problems.

In 2DMAT, the algorithms for solving the inverse problem can be selected as following algorithms:

- ``minsearch``

   Nelder-Mead method.

- ``mapper_mpi``

   Searching the entire search grid for a given parameter.

- ``bayes``

   Bayesian optimization.

- ``exchange``

   Sampling by the replica exchange Monte Carlo method.

- ``pamc``

   Sampling by the population annealing Monte Carlo method.

In this tutorial, we will first introduce how to run the direct problem solver ``sim-trhepd-rheed``.
Then we will instruct how to run ``minsearch`` , ``mapper_mpi``, ``bayes``, ``exchange``, and ``pamc``.
Hereinafter, we use ``py2dmat-sim-trhepd-rheed`` program included in 2DMAT-SIM-TRHEPD-RHEED with input files in TOML format.

At the end of the tutorial, we will explain how to write your own main program for analyses.


.. toctree::
   :maxdepth: 1

   sim_trhepd_rheed
   minsearch
   mapper
   bayes
   exchange
   pamc
   user_program
