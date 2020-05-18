# 2DMAT

## sample
version: 2020-05-18

### make a forward solver

``` bash
$ cd src/TRHEPD
$ make
```

### mapper

- Prerequists
  - Python2
  - mpi4py
  - numpy

``` bash
$ cd sample/original/mapper

# clean-up the previous result & make symbolic links
$ sh ./prepare.sh

# perform calculation
$ sh ./do.sh
```

### minsearch

- Prerequists
  - Python3
  - numpy
  - scipy

``` bash
$ cd sample/original/minsearch

# clean-up the previous result & make symbolic links
$ sh ./prepare.sh

# perform calculation
$ sh ./do.sh
```

