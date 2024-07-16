.. 2dmat documentation master file, created by
   sphinx-quickstart on Tue May 26 18:44:52 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

チュートリアル
==================================

順問題ソルバーとして用意されている ``sim_trhepd_rheed`` は、東北大学の花田貴先生によって開発された全反射高速(陽)電子回折(RHEED, TRHEPD)の解析ソフトウェアをベースに作成されています。

TRHEPDでは、与えられた原子位置に対して回折データのシミュレーションを行います。
これを原子位置から回折データへの順問題としたとき、実験で得られた回折データを再現するように原子位置を推定する逆問題を考えます。
2DMATでは、逆問題を解くためのアルゴリズムとして、以下の5つのアルゴリズムが用意されています。

- ``minsearch``

  Nelder-Mead法

- ``mapper_mpi``

  与えられたパラメータの探索グリッドを全探索

- ``bayes``

  ベイズ最適化

- ``exchange``

  レプリカ交換モンテカルロ法

- ``pamc``

  ポピュレーションアニーリング法

本チュートリアルでは、最初に順問題プログラム ``sim_trhepd_rheed`` の実行方法を説明した後、
``minsearch``, ``mapper_mpi``, ``bayes``, ``exchange``, ``pamc`` による逆問題解析の実行方法について順に説明します。以下では 2DMAT-SIM-TRHEPD-RHEED に付属の ``py2dmat-sim-trhepd-rheed`` プログラムを利用し、TOML形式のパラメータファイルを入力として解析を実行します。

チュートリアルの最後に、ユーザープログラムの項で、メインプログラムを自分で作成して使う方法を minsearch を例に説明します。

.. toctree::
   :maxdepth: 1

   sim_trhepd_rheed
   minsearch
   mapper
   bayes
   exchange
   pamc
   user_program
