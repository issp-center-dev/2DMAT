Introduction
=====================

What is 2DMAT ?
----------------------

2DMAT is a framework for applying a search algorithm to a direct problem solver to find the optimal solution. As the standard direct problem solver, the experimental data analysis software for two-dimensional material structure analysis is prepared. The direct problem solver gives the deviation between the experimental data and the calculated data obtained under the given parameters such as atomic positions as a loss function used in the inverse problem. The optimal parameters are estimated by minimizing the loss function using a search algorithm. For further use, the original direct problem solver or the search algorithm can be defined by users.
In the current version, for solving a direct problem, 2DMAT offers the wrapper of the solver for the total-reflection high-energy positron diffraction (TRHEPD) experiment[1, 2]. As algorithms, it offers the Nelder-Mead method[3], the grid search method[4], the Bayesian optimization method[5], and the replica exchange Monte Carlo method[6]. In the future, we plan to add other direct problem solvers and search algorithms in 2DMAT.

[1] As a review, see `Y. Fukaya, et al., J. Phys. D: Appl. Phys. 52, 013002 (2019) <https://iopscience.iop.org/article/10.1088/1361-6463/aadf14>`_.

[2] This software has been developed by T. Hanada in Tohoku University. `T. Hanada, H. Daimon, and S. Ino, Phys. Rev. B 51, 13320 (1995). <https://journals.aps.org/prb/abstract/10.1103/PhysRevB.51.13320>`_

[3] `K. Tanaka, T. Hoshi, I. Mochizuki, T. Hanada, A. Ichimiya, and T. Hyodo, Acta. Phys. Pol. A 137, 188 (2020) <http://przyrbwn.icm.edu.pl/APP/PDF/137/app137z2p25.pdf>`_.

[4] `K. Tanaka, I. Mochizuki, T. Hanada, A. Ichimiya, T. Hyodo, and T. Hoshi, JJAP Conf. Series, in press, arXiv:2002.12165 <https://arxiv.org/abs/2002.12165>`_.

[5] The python package `PHYSBO <https://www.pasums.issp.u-tokyo.ac.jp/physbo>`_ is used for Bayesian optimization.

[6] `K. Hukushima and K. Nemoto, J. Phys. Soc. Japan, 65, 1604 (1996) <https://journals.jps.jp/doi/10.1143/JPSJ.65.1604>`_,  `R. Swendsen and J. Wang, Phys. Rev. Lett. 57, 2607 (1986) <https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.57.2607>`_.

License
----------------------
|  This package is distributed under GNU General Public License version 3 (GPL v3).

Copyright (c) <2020-> The University of Tokyo. All rights reserved.

This software was developed with the support of "Project for advancement of software usability in materials science" of The Institute for Solid State Physics, The University of Tokyo.


Version Information
----------------------

- v1.0: 2021-03-11 
- v0.1: 2021-02-08


Main developers
----------------------
2DMAT has been developed by following members.

- v1.0, v0.1

  - Y. Motoyama (The Institute for Solid State Physics, The University of Tokyo)
  - K. Yoshimi (The Institute for Solid State Physics, The University of Tokyo)
  - T. Hoshi (Department of Applied Mathematics and Physics, Tottori University)
