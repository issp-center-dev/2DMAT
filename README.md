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
  - Python2 for original version
  - Python3 for new version
  - mpi4py
  - numpy

``` bash
$ cd sample/original/mapper

# clean-up the previous result & make symbolic links
$ sh ./prepare.sh

# perform calculation
$ sh ./do.sh
# or
$ sh ./do_original.sh
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
# or
$ sh ./do_original.sh
```

