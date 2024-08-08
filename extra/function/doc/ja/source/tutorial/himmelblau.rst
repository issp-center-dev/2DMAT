Himmelblau関数の最小化
================================

ここでは、2DMAT-Functions モジュールを用いたユーザプログラムを作成し、解析を行う方法を説明します。逆問題アルゴリズムは例としてNelder-Mead法を用います。


サンプルファイルの場所
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
サンプルファイルは ``sample/himmelblau`` にあります。
フォルダには以下のファイルが格納されています。

- ``main.py``

  メインプログラム。パラメータを ``input.toml`` ファイルから読み込んで解析を行う。

- ``input.toml``

  ``main.py`` で利用する入力パラメータファイル

- ``do.sh``

  本チュートリアルを一括計算するために準備されたスクリプト

- ``plot_colormap_2d.py``

  可視化ツール
  
以下、これらのファイルについて説明したのち、実際の計算結果を紹介します。

  
プログラムの説明
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``main.py`` は 2DMAT-Functions モジュールを用いて解析を行うシンプルなプログラムです。
プログラムの全体を以下に示します。

.. code-block:: python

    import numpy as np

    import py2dmat
    import py2dmat.algorithm.mapper_mpi as mapper
    from py2dmat.extra.function import Himmelblau

    info = py2dmat.Info.from_file("input.toml")
    solver = Himmelblau(info)
    runner = py2dmat.Runner(solver, info)

    alg = mapper.Algorithm(info, runner)
    alg.main()

プログラムではまず、必要なモジュールを import します。

- 2DMAT のメインモジュール ``py2dmat``

- 今回利用する逆問題解析アルゴリズム ``py2dmat.algorithm.mapper_mpi``

- 順問題ソルバーモジュール ``py2dmat.extra.function`` から Himmelblau クラス

次に、解析で利用するクラスのインスタンスを作成します。

- ``py2dmat.Info`` クラス

  パラメータを格納するクラスです。 ``from_file`` クラスメソッドに TOML ファイルのパスを渡して作成することができます。

- ``Himmelblau`` クラス

  2DMAT-Functions に用意されている Himmelblau関数のクラスです。Info クラスのインスタンスを渡して作成します。

- ``py2dmat.Runner`` クラス

  順問題ソルバーと逆問題解析アルゴリズムを繋ぐクラスです。Solver クラスのインスタンスおよび Info クラスのパラメータを渡して作成します。

- ``py2dmat.algorithm.mapper_mpi.Algorithm`` クラス

  逆問題解析アルゴリズムのクラスです。ここではグリッド全探索のクラスモジュール ``mapper_mpi`` を利用します。Runner のインスタンスを渡して作成します。

Solver, Runner, Algorithm の順にインスタンスを作成した後、Algorithm クラスの ``main()`` メソッドを呼んで解析を行います。
  
入力ファイルの説明
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

メインプログラム用の入力ファイル ``input.toml`` の例を以下に示します。
なお、アルゴリズムの種類を指定する ``algorithm.name`` パラメータの値は無視されます。

.. code-block:: toml

    [base]
    dimension = 2
    output_dir = "output"

    [algorithm]
    seed = 12345

    [algorithm.param]
    max_list = [6.0, 6.0]
    min_list = [-6.0, -6.0]
    num_list = [31, 31]

    [solver]

    [runner]
    [runner.log]
    interval = 20


計算実行
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

最初にサンプルファイルが置いてあるフォルダへ移動します。(以下、本ソフトウェアをダウンロードしたディレクトリ直下にいることを仮定します)

.. code-block::

    $ cd sample/himmelblau

メインプログラムを実行します。計算時間は通常のPCで数秒程度で終わります。

.. code-block::

    $ mpiexec -np 4 python3 main.py

ここではMPIを利用して4プロセスで計算を行っています。実行すると以下の様な出力がされます。

.. code-block::

    Make ColorMap
    Iteration : 1/240
    Iteration : 2/240
    Iteration : 3/240
    Iteration : 4/240
    Iteration : 5/240
    Iteration : 6/240
    Iteration : 7/240
    Iteration : 8/240
    Iteration : 9/240
    Iteration : 10/240
    ...

結果の可視化
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``ColorMap.txt`` を図示することで、関数の値が小さいパラメータがどこにあるかを推定することができます。そのような 2次元パラメータ空間のプロットを作成するプログラムが ``plot_colormap_2d.py`` に用意されています。

.. code-block::

    $ python3 plot_colormap_2d.py

上記を実行すると ``ColorMapFig.png`` が作成され、Himmelblau関数の関数値を表す等高線の上に、各グリッド点で評価した関数値がカラーマップとしてプロットされます。

.. figure:: ../../../common/img/himmelblau_mapper.*

    2次元パラメータ空間上での関数値のカラーマップ。

