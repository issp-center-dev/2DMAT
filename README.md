# 2DMAT -- Data-analysis software of quantum beam diffraction experiments for 2D material structure

2DMAT is a framework for applying a search algorithm to a direct problem solver to find the optimal solution.
As the standard direct problem solver, the experimental data analysis software for two-dimensional material structure analysis is prepared.
The direct problem solver gives the deviation between the experimental data and the calculated data obtained under the given parameters such as atomic positions as a loss function used in the inverse problem.
The optimal parameters are estimated by minimizing the loss function using a search algorithm.
For further use, the original direct problem solver or the search algorithm can be defined by users.
2DMAT offers wrappers of direct problem solvers for some of quantum beam diffraction experiments such as the total-reflection high-energy positron diffraction (TRHEPD) experiment.
As algorithms, it offers some minimizers such as the Nelder-Mead method and some samplers such as the population annealing Monte Carlo method.
In the future, we plan to add other direct problem solvers and search algorithms in 2DMAT.

| Branch |                Build status                 |                                       Documentation                                       |
| :----: | :-----------------------------------------: | :---------------------------------------------------------------------------------------: |
| [master][source/master] (latest) | [![master][ci/master/badge]][ci/master/uri] |        [![doc_en][doc/en/badge]][doc/en/uri] [![doc_ja][doc/ja/badge]][doc/ja/uri]        |
| [v2.1.0][source/stable] (latest stable) |                     --                      | [![doc_en][doc/en/badge]][doc/stable/en/uri] [![doc_ja][doc/ja/badge]][doc/stable/ja/uri] |

## py2dmat

`py2dmat` is a python framework library for solving inverse problems.
It also offers a driver script to solve the problem with predefined optimization algorithms
and direct problem solvers (`py2dmat` also means this script).

### Prerequists

- Required
  - python >= 3.6.8
  - numpy >= 1.14
  - tomli >= 1.2.0
- Optional
  - scipy
    - for `minsearch` algorithm
  - mpi4py
    - for `exchange` algorithm
  - physbo >= 1.0
    - for `bayes` algorithm

### Install

- From PyPI (Recommended)
  - `python3 -m pip install -U py2dmat`
    - If you install them locally, use `--user` option like `python3 -m pip install -U --user`
    - [`pipx`](https://pipxproject.github.io/pipx/) may help you from the dependency hell :p
- From Source (For developers)
  1. update `pip >= 19` by `python3 -m pip install -U pip`
  2. `python3 -m pip install 2DMAT_ROOT_DIRECTORY` to install `py2dmat` package and `py2dmat` command
    - `2DMAT_ROOT_DIRECTORY` means the directory including this `README.md` file.

### Simple Usage

- `py2dmat input.toml` (use the installed script)
- `python3 src/py2dmat_main.py input.toml` (use the raw script)
- For details of the input file, see the document.

## Files and directories of 2DMAT

- `src/`
  - source codes
- `script/`
  - utility scripts
- `sample/`
  - sample usages
- `doc/`
  - source codes of documents (manuals)
- `tests/`
  - for automatic test
- `LICENSE`
  - license terms (GNU GPL v3)
- `README.md`
  - this file
- `pyproject.toml`
  - metadata for `py2dmat`

## License

This package is distributed under GNU General Public License version 3 (GPL v3) or later.

## Copyright

© *2020- The University of Tokyo. All rights reserved.*
This software was developed with the support of "*Project for advancement of software usability in materials science*" of The Institute for Solid State Physics, The University of Tokyo.

[source/master]: https://github.com/issp-center-dev/2DMAT/
[source/stable]: https://github.com/issp-center-dev/2DMAT/tree/v2.1.0
[ci/master/badge]: https://github.com/issp-center-dev/2DMAT/workflows/Test/badge.svg?branch=master
[ci/master/uri]: https://github.com/issp-center-dev/2DMAT/actions?query=branch%3Amaster
[doc/en/badge]: https://img.shields.io/badge/doc-English-blue.svg
[doc/en/uri]: https://issp-center-dev.github.io/2DMAT/manual/master/en/index.html
[doc/ja/badge]: https://img.shields.io/badge/doc-Japanese-blue.svg
[doc/ja/uri]: https://issp-center-dev.github.io/2DMAT/manual/master/ja/index.html
[doc/stable/en/uri]: https://issp-center-dev.github.io/2DMAT/manual/v2.1.0/en/index.html
[doc/stable/ja/uri]: https://issp-center-dev.github.io/2DMAT/manual/v2.1.0/ja/index.html
