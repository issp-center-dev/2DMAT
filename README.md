# 2DMAT

Data-analysis software of quantum beam diffraction experiments for 2D material structure

2DMATは，順問題ソルバーに対して探索アルゴリズムを適用して最適解を探すためのフレームワークです.
順問題ソルバーはユーザー自身で定義することが可能です.
標準的な順問題ソルバーとしては2次元物質構造解析向け実験データ解析ソフトウェアが用意されています.
順問題ソルバーでは原子位置などをパラメータとし得られたデータと実験データとのずれを損失関数として与えます.
探索アルゴリズムを組み合わせ, この損失関数を最小化することで, 最適なパラメータを推定します.
現バージョンでは, 順問題ソルバーとして量子ビーム回折実験の全反射高速陽電子回折実験（Total-reflection high-energy positron diffraction ,TRHEPD，トレプト）に対応しており, 探索アルゴリズムはNelder-Mead法, グリッド型探索法, ベイズ最適化, レプリカ交換モンテカルロ法が実装されています.
今後は, 本フレームワークをもとにより多くの順問題ソルバーおよび探索アルゴリズムを実装していく予定です.

| Branch | Build status | Documentation |
| :-: | :-: | :-: |
| master | [![master](https://github.com/issp-center-dev/2DMAT/workflows/Test/badge.svg?branch=master)](https://github.com/issp-center-dev/2DMAT/actions?query=branch%3Amaster) | [![doc_ja](https://img.shields.io/badge/doc-Japanese-blue.svg)](https://issp-center-dev.github.io/2DMAT/manual/master/ja/index.html) |

## py2dmat

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
