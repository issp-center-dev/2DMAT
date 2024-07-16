ユーザープログラムによる解析
================================

ここでは、2DMAT-LEED モジュールを用いたユーザープログラムを作成し、解析を行う方法を説明します。逆問題アルゴリズムは例としてNelder-Mead法を用います。


サンプルファイルの場所
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
サンプルファイルは ``sample/user_program`` にあります。
フォルダには以下のファイルが格納されています。

- ``simple.py``

  メインプログラム。パラメータを ``input.toml`` ファイルから読み込んで解析を行う。

- ``input.toml``

  ``simple.py`` で利用する入力パラメータファイル

- ``base/``

  メインプログラムでの計算を進めるための参照ファイルを格納するディレクトリ。参照ファイルは ``exp.d``, ``rfac.d``, ``short.t``, ``tleed.o``, ``tleed4.i``, ``tleed5.i`` .

- ``ref.txt``

  本チュートリアルで求めたい回答が記載されたファイル

- ``simple2.py``

  メインプログラムの別バージョン。パラメータを dict 形式でスクリプト中に埋め込んでいる。

- ``prepare.sh``, ``do.sh``

  本チュートリアルを一括計算するために準備されたスクリプト

以下、これらのファイルについて説明したのち、実際の計算結果を紹介します。

プログラムの説明
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``simple.py`` は 2DMAT-LEED モジュールを用いて解析を行うシンプルなプログラムです。
プログラムの全体を以下に示します。

.. code-block:: python

    import py2dmat
    import py2dmat.algorithm.min_search
    import leed
    
    info = py2dmat.Info.from_file("input.toml")
    
    solver = leed.Solver(info)
    runner = py2dmat.Runner(solver, info)
    alg = py2dmat.algorithm.min_search.Algorithm(info, runner)
    alg.main()

プログラムではまず、必要なモジュールを import します。

- 2DMAT のメインモジュール ``py2dmat``

- 今回利用する逆問題解析アルゴリズム ``py2dmat.algorithm.min_search``

- 順問題ソルバーモジュール ``leed``

次に、解析で利用するクラスのインスタンスを作成します。

- ``py2dmat.Info`` クラス

  パラメータを格納するクラスです。 ``from_file`` クラスメソッドに TOML ファイルのパスを渡して作成することができます。

- ``leed.Solver`` クラス

  2DMAT-LEED モジュールの順問題ソルバーです。Info クラスのインスタンスを渡して作成します。

- ``py2dmat.Runner`` クラス

  順問題ソルバーと逆問題解析アルゴリズムを繋ぐクラスです。Solver クラスのインスタンスおよび Info クラスのパラメータを渡して作成します。

- ``py2dmat.algorithm.min_search.Algorithm`` クラス

  逆問題解析アルゴリズムのクラスです。ここでは Nelder-Mead法による最適化アルゴリズムのクラスモジュール ``min_search`` を利用します。Runner のインスタンスをわたして作成します。

Solver, Runner, Algorithm の順にインスタンスを作成した後、Algorithm クラスの ``main()`` メソッドを呼んで解析を行います。

上記のプログラムでは、入力パラメータを TOML形式のファイルから読み込む形ですが、パラメータを dict 形式で渡すこともできます。
``simple2.py`` はパラメータをプログラム中に埋め込む形式で記述したものです。以下にプログラムの全体を記載します。

.. code-block:: python

    import py2dmat
    import py2dmat.algorithm.min_search
    import leed
    
    params = {
        "base": {
            "dimension": 2,
            "output_dir": "output",
        },
        "solver": {
            "config": {
                "path_to_solver": "./leedsatl/satl2.exe",
            },
            "reference": {
                "path_to_base_dir": "./base",
            },
        },
        "algorithm": {
            "label_list": ["z1", "z2"],
            "param": {
                "min_list": [-0.5, -0.5],
                "max_list": [0.5,  0.5],
                "initial_list": [-0.1, 0.1],
            },
             
        },
    }
    
    info = py2dmat.Info(params)
    
    solver = leed.Solver(info)
    runner = py2dmat.Runner(solver, info)
    alg = py2dmat.algorithm.min_search.Algorithm(info, runner)
    alg.main()

dict 形式のパラメータを渡して Info クラスのインスタンスを作成します。
同様に、パラメータをプログラム内で生成して渡すこともできます。

入力ファイルの説明
~~~~~~~~~~~~~~~~~~~
メインプログラム用の入力ファイル ``input.toml`` に、順問題ソルバーおよび逆問題解析アルゴリズムのパラメータを指定します。 ``base`` および ``solver`` セクションの内容は前述のグリッド型探索の場合と同じです。
逆問題解析アルゴリズムについては、Nelder-Mead法のパラメータを algorithm.param の項目に指定します。なお、アルゴリズムの種類を指定する ``algorithm.name`` パラメータの値は無視されます。


- ``min_list``, ``max_list`` は探索領域の指定で、領域の下端と上端を変数についてのリストの形式で与えます。

- ``initial_list`` には初期値を指定します。


計算実行
~~~~~~~~~~~~

最初にサンプルファイルが置いてあるフォルダへ移動します(以下、本ソフトウェアをダウンロードしたデ
ィレクトリ直下にいることを仮定します).

.. code-block::

    $ cd sample/user_program

グリッド探索の例でコンパイルした SATLEED プログラムをコピーします。作成していない場合は、
``sample/mapper`` ディレクトリの中で ``sh setup.sh`` を実行し、 ``leedsatl/satl1.exe`` と ``leedsatl/satl2.exe`` を作ります。

.. code-block::

    $ mkdir leedsatl
    $ cp ../mapper/leedsatl/satl2.exe ./leedsatl

メインプログラムを実行します。(計算時間は通常のPCで数秒程度で終わります。)
    
.. code-block::

    $ python3 simple.py | tee log.txt

実行すると、以下の様な出力がされます。

.. code-block::

    Optimization terminated successfully.
             Current function value: 0.157500
             Iterations: 29
             Function evaluations: 63
    iteration: 29
    len(allvecs): 30
    step: 0
    allvecs[step]: [-0.1  0.1]
    step: 1
    allvecs[step]: [-0.1  0.1]
    step: 2
    allvecs[step]: [-0.1  0.1]
    step: 3
    allvecs[step]: [-0.1  0.1]
    step: 4
    allvecs[step]: [-0.1  0.1]
    step: 5
    allvecs[step]: [-0.0375  -0.05625]
    step: 6
    allvecs[step]: [-0.0375  -0.05625]
    step: 7
    allvecs[step]: [-0.0375  -0.05625]
    ...

``z1``, ``z2`` に各ステップでの候補パラメータと、その時の ``R-factor`` が出力されます。
最終的に推定されたパラメータは、 ``output/res.dat`` に出力されます。今の場合、

.. code-block::

    fx = 0.1575
    z1 = -0.01910402104258537
    z2 = 0.10217590294778345

となります。リファレンス ref.txt が再現されていることが分かります。

なお、一連の計算を行う ``do.sh`` スクリプトが用意されています。
