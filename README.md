# 2DMAT

## py2dmat

- Prerequists python packages
  - numpy >= 1.17
  - toml
- Optional python packages
  - scipy
    - for `minsearch` algorithm
  - mpi4py
    - for `exchange` algorithm
  - physbo >= 0.3
    - for `bayes` algorithm
- Install from source
  1. update `pip >= 19` by `python3 -m pip install -U pip`
  2. `python3 -m pip install 2DMAT_ROOT_DIRECTORY` to install `py2dmat` package and `py2dmat` command
    - If you install them locally, use `--user` option like `python3 -m pip install --user`
    - [`pipx`](https://pipxproject.github.io/pipx/) may help you from the dependency hell :p
- Simple usage
  - `py2dmat input.toml` (use the installed script)
  - `python3 src/py2dmat_main.py input.toml` (use the raw script)
  - For details of the input file, see the document.

## samples

`sample` directory has some sample scripts.

``` bash
$ cd sample/py2dmat/exchange-rosenbrock

# clean-up the previous result & make symbolic links
$ sh ./prepare.sh

# perform calculation
$ sh ./do.sh
```
