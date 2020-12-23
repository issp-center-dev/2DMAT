# 2DMAT

## sample
version: 2020-05-18

### make a forward TRHEPD solver

- Prerequists
  - Fortran compiler

``` bash
$ cd src/TRHEPD
$ make
```

### py2dmat

- Prerequists python packages
  - numpy
  - toml
- Optional python packages
  - scipy
    - for `minsearch` algorithm
  - mpi4py
    - for `exchange` algorithm
  - physbo
    - for `bayes` algorithm

``` bash
$ cd sample/py2dmat/mapper

# clean-up the previous result & make symbolic links
$ sh ./prepare.sh

# perform calculation
$ sh ./do.sh
```

