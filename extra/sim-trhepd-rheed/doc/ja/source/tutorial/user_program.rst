ユーザープログラムによる解析
================================

ここでは、2DMAT-SIM-TRHEPD-RHEED モジュールを用いたユーザプログラムを作成し、解析を行う方法を説明します。逆問題アルゴリズムは例としてNelder-Mead法を用います。


サンプルファイルの場所
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
サンプルファイルは ``sample/single_beam/user_program`` にあります。
フォルダには以下のファイルが格納されています。

- ``simple.py``

  メインプログラム。パラメータを ``input.toml`` ファイルから読み込んで解析を行う。

- ``input.toml``

  ``simple.py`` で利用する入力パラメータファイル

- ``experiment.txt``, ``template.txt``

  メインプログラムでの計算を進めるための参照ファイル

- ``ref.txt``

  本チュートリアルで求めたい回答が記載されたファイル

- ``simple2.py``

  メインプログラムの別バージョン。パラメータを dict 形式でスクリプト内に埋め込んでいる。

- ``prepare.sh`` , ``do.sh``

  本チュートリアルを一括計算するために準備されたスクリプト

以下、これらのファイルについて説明したのち、実際の計算結果を紹介します。

  
プログラムの説明
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``simple.py`` は 2DMAT-SIM-TRHEPD-RHEED モジュールを用いて解析を行うシンプルなプログラムです。
プログラムの全体を以下に示します。

.. code-block:: python

    import numpy as np

    import py2dmat
    import py2dmat.algorithm.min_search
    import sim_trhepd_rheed

    info = py2dmat.Info.from_file("input.toml")

    solver = sim_trhepd_rheed.Solver(info)
    runner = py2dmat.Runner(solver, info)
    alg = py2dmat.algorithm.min_search.Algorithm(info, runner)
    alg.main()

プログラムではまず、必要なモジュールを import します。

- 2DMAT のメインモジュール ``py2dmat``

- 今回利用する逆問題解析アルゴリズム ``py2dmat.algorithm.min_search``

- 順問題ソルバーモジュール ``sim_trhepd_rheed``

次に、解析で利用するクラスのインスタンスを作成します。

- ``py2dmat.Info`` クラス

  パラメータを格納するクラスです。 ``from_file`` クラスメソッドに TOML ファイルのパスを渡して作成することができます。

- ``sim_trhepd_rheed.Solver`` クラス

  2DMAT-SIM-TRHEPD-RHEED モジュールの順問題ソルバーです。Info クラスのインスタンスを渡して作成します。

- ``py2dmat.Runner`` クラス

  順問題ソルバーと逆問題解析アルゴリズムを繋ぐクラスです。Solver クラスのインスタンスおよび Info クラスのパラメータを渡して作成します。

- ``py2dmat.algorithm.min_search.Algorithm`` クラス

  逆問題解析アルゴリズムのクラスです。ここでは Nelder-Mead法による最適化アルゴリズムのクラスモジュール ``min_search`` を利用します。Runner のインスタンスを渡して作成します。

Solver, Runner, Algorithm の順にインスタンスを作成した後、Algorithm クラスの ``main()`` メソッドを呼んで解析を行います。
  
上記のプログラムでは、入力パラメータを TOML形式のファイルから読み込む形ですが、パラメータを dict 形式で渡すこともできます。
``simple2.py`` はパラメータをプログラム中に埋め込む形式で記述したものです。以下にプログラムの全体を記載します。

.. code-block:: python

    import numpy as np

    import py2dmat
    import py2dmat.algorithm.min_search
    import sim_trhepd_rheed

    params = {
        "base": {
            "dimension": 3,
            "output_dir": "output",
        },
        "solver": {
            "run_scheme": "subprocess",
            "generate_rocking_curve": True,
            "config": {
                "cal_number": [1],
            },
            "param": {
                "string_list": ["value_01", "value_02", "value_03"],
            },
            "reference": {
                "path": "experiment.txt",
                "exp_number": [1],
            },
            "post": {
                "normalization": "TOTAL",
            },
        },
        "algorithm": {
            "label_list": ["z1", "z2", "z3"],
            "param": {
                "min_list": [ 0.0, 0.0, 0.0 ],
                "max_list": [ 10.0, 10.0, 10.0 ],
                "initial_list": [ 5.25, 4.25, 3.50],
            },
        },
    }

    info = py2dmat.Info(params)

    solver = sim_trhepd_rheed.Solver(info)
    runner = py2dmat.Runner(solver, info)
    alg = py2dmat.algorithm.min_search.Algorithm(info, runner)
    alg.main()

dict 形式のパラメータを渡して Info クラスのインスタンスを作成します。
同様に、パラメータをプログラム内で生成して渡すこともできます。

入力ファイルの説明
~~~~~~~~~~~~~~~~~~~
メインプログラム用の入力ファイル ``input.toml`` は前述のNelder-Mead法による最適化で用いたのと同じファイルを利用できます。
なお、アルゴリズムの種類を指定する ``algorithm.name`` パラメータの値は無視されます。

その他、 ``template.txt``, ``experiment.txt`` ファイルは前述の tutorial と同様です。

計算実行
~~~~~~~~~~~~

最初にサンプルファイルが置いてあるフォルダへ移動します(以下、本ソフトウェアをダウンロードしたディレクトリ直下にいることを仮定します).

.. code-block::

    $ cd sample/single_beam/user_program

``bulk.exe`` と ``surf.exe`` をコピーします。

.. code-block::

    $ cp ../../sim-trhepd-rheed/src/bulk.exe .
    $ cp ../../sim-trhepd-rheed/src/surf.exe .

``bulk.exe`` を実行し、 ``bulkP.b`` を作成します。

.. code-block::

    $ ./bulk.exe

そのあとに、メインプログラムを実行します(計算時間は通常のPCで数秒程度で終わります)。

.. code-block::

    $ python3 simple.py | tee log.txt

実行すると、以下の様な出力がされます。

.. code-block::

    Read experiment.txt
    z1 =  5.25000
    z2 =  4.25000
    z3 =  3.50000
    [' 5.25000', ' 4.25000', ' 3.50000']
    PASS : degree in lastline = 7.0
    PASS : len(calculated_list) 70 == len(convolution_I_calculated_list)70
    R-factor = 0.015199251773721183
    z1 =  5.50000
    z2 =  4.25000
    z3 =  3.50000
    [' 5.50000', ' 4.25000', ' 3.50000']
    PASS : degree in lastline = 7.0
    PASS : len(calculated_list) 70 == len(convolution_I_calculated_list)70
    R-factor = 0.04380131351780189
    z1 =  5.25000
    z2 =  4.50000
    z3 =  3.50000
    [' 5.25000', ' 4.50000', ' 3.50000']
    ...

``z1``, ``z2``, ``z3`` に各ステップでの候補パラメータと、その時の ``R-factor`` が出力されます。
また各ステップでの計算結果は ``output/0/LogXXXX_YYYY`` (XXXX, YYYYはステップ数)のフォルダに出力されます。
最終的に推定されたパラメータは、 ``output/res.dat`` に出力されます。今の場合、

.. code-block::

    z1 = 5.230524973874179
    z2 = 4.370622919269477
    z3 = 3.5961444501081647

となります。リファレンス ref.txt が再現されていることが分かります。

なお、一連の計算を行う ``do.sh`` スクリプトが用意されています。
