Introduction
================================

What is 2DMAT ?
--------------------------------

2DMAT is a framework for applying a search algorithm to a direct problem solver to find the optimal solution.
As the standard direct problem solver, the experimental data analysis software for two-dimensional material structure analysis is prepared.
The direct problem solver gives the deviation between the experimental data and the calculated data obtained under the given parameters such as atomic positions as a loss function used in the inverse problem.
The optimal parameters are estimated by minimizing the loss function using a search algorithm. For further use, the original direct problem solver or the search algorithm can be defined by users.
In the current version, for solving a direct problem, 2DMAT offers the wrapper of the solver for the total-reflection high-energy positron diffraction (TRHEPD), the surface X-ray diffraction (Functions), and the low-energy electron diffraction (LEED).
As algorithms, it offers the Nelder-Mead method, the grid search method, the Bayesian optimization method, the replica exchange Monte Carlo method, and the population annealing Monte Carlo method.


What is 2DMAT-Functions ?
--------------------------------

``2DMAT-Functions`` provides implementation of several analytical functions for the direct problems of 2DMAT.
The major use of this module is to test and benchmark the optimization algorithms of 2DMAT, while it may be useful as a template when the users write their own direct problem solvers.

It was originally developed as a component of 2DMAT v2.x, and has been restructured as a separate module to be used with 2DMAT.



License
--------------------------------
|  This package is distributed under GNU General Public License version 3 (GPL v3).

Copyright (c) <2020-> The University of Tokyo. All rights reserved.

This software was developed with the support of "Project for advancement of software usability in materials science" of The Institute for Solid State Physics, The University of Tokyo.
We hope that you cite the following reference when you publish the results using 2DMAT:

"Data-analysis software framework 2DMAT and its application to experimental measurements for two-dimensional material structures", Y. Motoyama, K. Yoshimi, I. Mochizuki, H. Iwamoto, H. Ichinose, and T. Hoshi, `Computer Physics Communications 280, 108465 (2022). <https://doi.org/10.1016/j.cpc.2022.108465>`_

Bibtex:

| @article{MOTOYAMA2022108465,
|   title = {Data-analysis software framework 2DMAT and its application to experimental measurements for two-dimensional material structures},
|   journal = {Computer Physics Communications},
|   volume = {280},
|   pages = {108465},
|   year = {2022},
|   issn = {0010-4655},
|   doi = {https://doi.org/10.1016/j.cpc.2022.108465},
|   url = {https://www.sciencedirect.com/science/article/pii/S0010465522001849},
|   author = {Yuichi Motoyama and Kazuyoshi Yoshimi and Izumi Mochizuki and Harumichi Iwamoto and Hayato Ichinose and Takeo Hoshi}
| }


Version Information
--------------------------------

2DMAT-Functions

- v1.0.0: 2024-XX-XX

2DMAT

- v3.0.0: 2024-XX-XX
- v2.1.0: 2022-04-08
- v2.0.0: 2022-01-17
- v1.0.1: 2021-04-15 
- v1.0.0: 2021-03-12 
- v0.1.0: 2021-02-08


Main developers
--------------------------------

2DMAT has been developed by following members.

- v3.0.0 -

  - Y. Motoyama (The Institute for Solid State Physics, The University of Tokyo)
  - K. Yoshimi (The Institute for Solid State Physics, The University of Tokyo)
  - T. Aoyama (The Institute for Solid State Physics, The University of Tokyo)
  - T. Hoshi (National Institute for Fusion Science)

- v2.0.0 -

  - Y. Motoyama (The Institute for Solid State Physics, The University of Tokyo)
  - K. Yoshimi (The Institute for Solid State Physics, The University of Tokyo)
  - H. Iwamoto (Department of Applied Mathematics and Physics, Tottori University)
  - T. Hoshi (Department of Applied Mathematics and Physics, Tottori University)

- v0.1.0 - v1.0.1

  - Y. Motoyama (The Institute for Solid State Physics, The University of Tokyo)
  - K. Yoshimi (The Institute for Solid State Physics, The University of Tokyo)
  - T. Hoshi (Department of Applied Mathematics and Physics, Tottori University)
