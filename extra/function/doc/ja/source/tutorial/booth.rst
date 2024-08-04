関数の追加
================================

ここでは、2DMAT-Functions モジュールを用いて、ユーザが新しい関数を作成して解析を行う手順を説明します。例として次の Booth 関数

.. math::

   f(x,y) = (x + 2 y - 7) ^2 + (2 x + y - 5) ^2

を追加してみます。この関数の最小値は :math:`f(1,3) = 0` です。


サンプルファイルの場所
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
サンプルファイルは ``sample/booth`` にあります。
フォルダには以下のファイルが格納されています。

- ``booth.py``

  Booth関数を計算する順問題ソルバーを定義する

- ``main.py``

  メインプログラム。パラメータを ``input.toml`` ファイルから読み込んで解析を行う

- ``input.toml``

  ``simple.py`` で利用する入力パラメータファイル

- ``do.sh``

  本チュートリアルを一括計算するために準備されたスクリプト

以下、これらのファイルについて説明したのち、実際の計算結果を紹介します。

  
プログラムの説明
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``booth.py`` では、2DMAT-Functions を利用して Booth 関数を計算する順問題ソルバークラスを定義します。プログラムの全体を以下に示します。

.. code-block:: python

    import numpy as np
    import py2dmat.extra.function

    class Booth(py2dmat.extra.function.Solver):
        def evaluate(self, xs: np.ndarray, args=()):
            assert xs.shape[0] == 2
            x, y = xs
            fx = (x + 2 * y - 7)**2 + (2 * x + y - 5)**2
            return fx

プログラムでは、まず必要なモジュールを import します。
``py2dmat.extra.function`` は 2DMAT-Functions モジュールです。

次に、2DMAT-Functions の ``Solver`` クラスを基底クラスとして ``Booth`` クラスを作成します。
関数値を評価するメソッドを ``evaluate(self, xs, args) -> float`` として定義します。
``evaluate`` の引数は、パラメータ値を表す ``numpy.ndarray`` 型の引数 ``xs`` と、 ``Tuple`` 型のオプションパラメータ ``args`` です。
``args`` はステップ数 ``step`` と n巡目を表す ``set`` からなり、必要に応じてクラス内で使用します。


``main.py`` は Booth クラスを用いて解析を行うシンプルなプログラムです。

.. code-block:: python

    import numpy as np

    import py2dmat
    import py2dmat.algorithm.min_search as min_search
    from booth import Booth

    info = py2dmat.Info.from_file("input.toml")
    solver = Booth(info)
    runner = py2dmat.Runner(solver, info)

    alg = min_search.Algorithm(info, runner)
    alg.main()

プログラム中ではまず、解析で利用するクラスのインスタンスを作成します。

- ``py2dmat.Info`` クラス

  パラメータを格納するクラスです。 ``from_file`` クラスメソッドに TOML ファイルのパスを渡して作成することができます。

- ``Booth`` クラス

  上記で作成した booth.py から Booth クラスを import してインスタンスを作成します。

- ``py2dmat.Runner`` クラス

  順問題ソルバーと逆問題解析アルゴリズムを繋ぐクラスです。Solver クラスのインスタンスおよび Info クラスのパラメータを渡して作成します。

- ``py2dmat.algorithm.min_search.Algorithm`` クラス

  逆問題解析アルゴリズムのクラスです。ここでは Nelder-Mead法による最適化アルゴリズムのクラスモジュール ``min_search`` を利用します。Runner のインスタンスを渡して作成します。

Solver, Runner, Algorithm の順にインスタンスを作成した後、Algorithm クラスの ``main()`` メソッドを呼んで解析を行います。

入力ファイルの説明
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

メインプログラム用の入力ファイル ``input.toml`` の例を以下に示します。

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
~~~~~~~~~~~~

最初にサンプルファイルが置いてあるフォルダへ移動します。

.. code-block::

    $ cd sample/booth

メインプログラムを実行します。計算時間は通常のPCで数秒程度で終わります。

.. code-block::

    $ python3 main.py | tee log.txt

実行すると、以下の様な出力がされます。

.. code-block::

    Optimization terminated successfully.
             Current function value: 0.000000
             Iterations: 44
             Function evaluations: 82
    iteration: 44
    len(allvecs): 45
    step: 0
    allvecs[step]: [ 5.15539311 -2.20349335]
    step: 1
    allvecs[step]: [ 4.65539311 -1.82849335]
    step: 2
    allvecs[step]: [ 4.40539311 -1.26599335]
    step: 3
    allvecs[step]: [ 3.28039311 -0.73474335]
    step: 4
    allvecs[step]: [2.21789311 0.65588165]
    step: 5
    allvecs[step]: [2.21789311 0.65588165]
    ...
    step: 42
    allvecs[step]: [0.99997645 3.00001226]
    step: 43
    allvecs[step]: [0.99997645 3.00001226]
    end of run
    Current function value: 1.2142360244883376e-09
    Iterations: 44
    Function evaluations: 82
    Solution:
    x1 = 0.9999764520155436
    x2 = 3.000012263854959


``x1``, ``x2`` に各ステップでの候補パラメータと、その時の目的関数の値が出力されます。
最終的に推定されたパラメータは、 ``output/res.dat`` に出力されます。今の場合、

.. code-block::

    fx = 1.2142360244883376e-09
    x1 = 0.9999764520155436
    x2 = 3.000012263854959

となり、最小値が再現されていることがわかります。
なお、一連の計算を行う ``do.sh`` スクリプトが用意されています。
