# 2DMAT

## sample
version: 2021-01-19

### make a forward TRHEPD solver

- Prerequists
  - Fortran compiler

``` bash
$ cd src/TRHEPD
$ make
```

### py2dmat

- Prerequists python packages
  - numpy >= 1.17
  - toml
- Optional python packages
  - scipy
    - for `minsearch` algorithm
  - mpi4py
    - for `exchange` algorithm
  - physbo >= 0.2
    - for `bayes` algorithm

``` bash
$ cd sample/py2dmat/mapper

# clean-up the previous result & make symbolic links
$ sh ./prepare.sh

# perform calculation
$ sh ./do.sh
```

