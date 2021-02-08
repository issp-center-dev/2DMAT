# 2DMAT -- Data-analysis software of quantum beam diffraction experiments for 2D material structure

2DMAT is a framework for applying a search algorithm to a direct problem solver to find the optimal solution. As the standard direct problem solver, the experimental data analysis software for two-dimensional material structure analysis is prepared. The direct problem solver gives the deviation between the experimental data and the calculated data obtained under the given parameters such as atomic positions as a loss function used in the inverse problem. The optimal parameters are estimated by minimizing the loss function using a search algorithm. For further use, the original direct problem solver or the search algorithm can be defined by users.
In the current version, for solving a direct problem, 2DMAT offers the wrapper of the solver for the total-reflection high-energy positron diffraction (TRHEPD) experiment. As algorithms, it offers the Nelder-Mead method, the grid search method, the Bayesian optimization method, and the replica exchange Monte Carlo method. In the future, we plan to add other direct problem solvers and search algorithms in 2DMAT.

| Branch | Build status | Documentation |
| :-: | :-: | :-: |
| master | [![master](https://github.com/issp-center-dev/2DMAT/workflows/Test/badge.svg?branch=master)](https://github.com/issp-center-dev/2DMAT/actions?query=branch%3Amaster) | [![doc_ja](https://img.shields.io/badge/doc-Japanese-blue.svg)](https://issp-center-dev.github.io/2DMAT/manual/master/ja/index.html) |

## py2dmat

`py2dmat` is a python framework library for solving inverse problems.
It also offers a driver script to solve the problem with predefined algorithms
and solvers (`py2dmat` also means this script).

### Prerequists

- Required
  - python >= 3.6
  - numpy >= 1.17
  - toml
- Optional
  - scipy
    - for `minsearch` algorithm
  - mpi4py
    - for `exchange` algorithm
  - physbo >= 0.3
    - for `bayes` algorithm

### Install

- From PyPI (Recommended)
  - `python3 -m pip install py2dmat`
    - If you install them locally, use `--user` option like `python3 -m pip install --user`
    - [`pipx`](https://pipxproject.github.io/pipx/) may help you from the dependency hell :p
- From Source (For developers)
  1. update `pip >= 19` by `python3 -m pip install -U pip`
  2. `python3 -m pip install 2DMAT_ROOT_DIRECTORY` to install `py2dmat` package and `py2dmat` command

### Simple Usage

- `py2dmat input.toml` (use the installed script)
- `python3 src/py2dmat_main.py input.toml` (use the raw script)
- For details of the input file, see the document.

## License

This package is distributed under GNU General Public License version 3 (GPL v3) or later.

## Copyright

© *2020- The University of Tokyo. All rights reserved.*
This software was developed with the support of \"*Project for advancement of software usability in materials science*\" of The Institute for Solid State Physics, The University of Tokyo. 
