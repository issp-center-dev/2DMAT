ユーザープログラムによる解析
================================

ここでは、2DMAT-SXRD モジュールを用いたユーザープログラムを作成し、解析を行う方法を説明します。逆問題解析アルゴリズムには例としてNelder-Mead法を用います。

サンプルファイルの場所
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
サンプルファイルは ``sample/user_program`` にあります。
ディレクトリには以下のファイルが格納されています。

- ``simple.py``

  メインプログラム。パラメータを ``input.toml`` ファイルから読み込んで解析を行う。

- ``input.toml``

  ``simple.py`` で利用する入力パラメータファイル

- ``sic111-r3xr3.blk``, ``sic111-r3xr3_f.dat``

  メインプログラムでの計算を進めるための参照ファイル

- ``ref_res.txt``, ``ref_SimplexData.txt``

  本チュートリアルで求めたい回答を記載したファイル

- ``simple.py``

  メインプログラムの別バージョン。パラメータを dict 形式でスクリプト内に埋め込んでいる。


以下、これらのファイルについて説明したのち、実際の計算結果を紹介します。

プログラムの説明  
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``simple.py`` は 2DMAT-SXRD モジュールを用いて解析を行うシンプルなプログラムです。
プログラム全体を以下に示します。

.. code-block:: python

   import numpy as np

   import py2dmat
   import py2dmat.algorithm.min_search
   import sxrd

   info = py2dmat.Info.from_file("input.toml")

   solver = sxrd.Solver(info)
   runner = py2dmat.Runner(solver, info)
   alg = py2dmat.algorithm.min_search.Algorithm(info, runner)
   alg.main()

   
プログラムではまず、必要なモジュールを import します。

- 2DMAT のメインモジュール ``py2dmat``

- 今回利用する逆問題解析アルゴリズム ``py2dmat.algorithm.min_search``

- 順問題ソルバーモジュール ``sxrd``

次に、解析で利用するクラスのインスタンスを作成します。

- ``py2dmat.Info`` クラス

  パラメータを格納するクラスです。 ``from_file`` クラスメソッドに TOML ファイルのパスを渡して作成することができます。

- ``sxrd.Solver`` クラス

  2DMAT-SXRD モジュールの順問題ソルバーです。Info クラスのインスタンスを渡して作成します。

- ``py2dmat.Runner`` クラス

  順問題ソルバーと逆問題解析アルゴリズムを繋ぐクラスです。Solver クラスのインスタンスおよび Info クラスのパラメータを渡して作成します。

- ``py2dmat.algorithm.min_search.Algorithm`` クラス

  逆問題解析アルゴリズムのクラスです。ここでは Nelder-Mead 法による最適化アルゴリズムのクラスモジュール ``min_search`` を利用します。Runnder のインスタンスを渡して作成します。

Solver, Runner, Algorithm の順にインスタンスを作成した後、Algorithm クラスの ``main()`` メソッドを呼んで解析を行います。

上記のプログラムでは、入力パラメータを TOML形式のファイルから読み込む形ですが、パラメータを dict 形式で渡すこともできます。
``simple2.py`` はパラメータをプログラム中に埋め込む形で記述したものです。以下にプログラムの全体を記載します。

.. code-block:: python

    import numpy as np
    
    import py2dmat
    import py2dmat.algorithm.min_search
    import sxrd
    
    param = {
        "base": {
            "dimension": 2,
            "output_dir": "output",
        },
        "solver": {
            "config": {
                "sxrd_exec_file": "sxrdcalc",
                "bulk_struc_in_file": "sic111-r3xr3.blk",
            },
            "param": {
                "scale_factor": 1.0,
                "type_vector": [1, 2],
                "domain": [
                    {
                        "domain_occupancy": 1.0,
                        "atom": [
                            {
                                "name": "Si",
                                "pos_center": [0.00000000, 0.00000000, 1.00000000],
                                "DWfactor": 0.0,
                                "occupancy": 1.0,
                                "displace_vector": [[1, 0.0, 0.0, 1.0]]
                            },
                            {
                                "name": "Si",
                                "pos_center": [0.33333333, 0.66666667, 1.00000000],
                                "DWfactor": 0.0,
                                "occupancy": 1.0,
                                "displace_vector": [[1, 0.0, 0.0, 1.0]]
                            },
                            {
                                "name": "Si",
                                "pos_center": [0.66666667, 0.33333333, 1.00000000],
                                "DWfactor": 0.0,
                                "occupancy": 1.0,
                                "displace_vector": [[1, 0.0, 0.0, 1.0]]
                            },
                            {
                                "name": "Si",
                                "pos_center": [0.33333333, 0.33333333, 1.20000000],
                                "DWfactor": 0.0,
                                "occupancy": 1.0,
                                "displace_vector": [[2, 0.0, 0.0, 1.0]]
                            },
                        ],
                    },
                ],
            },
            "reference": {
                "f_in_file": "sic111-r3xr3_f.dat",
            },
        },
        "algorithm": {
            "label_list": ["z1", "z2"],
            "param": {
                "min_list": [-0.2, -0.2],
                "max_list": [ 0.2,  0.2],
                "initial_list": [ 0.0, 0.0 ],
            },
        },
    }
    
    info = py2dmat.Info(param)
    
    solver = sxrd.Solver(info)
    runner = py2dmat.Runner(solver, info)
    alg = py2dmat.algorithm.min_search.Algorithm(info, runner)
    alg.main()

dict 形式のパラメータを渡して Info クラスのインスタンスを作成します。
同様に、パラメータをプログラム内で生成して渡すこともできます。

入力ファイルの説明  
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

メインプログラム用の入力ファイル ``input.toml`` は前述のNelder-Mead法による最適化で用いたのと同じファイルを利用できます。
なお、アルゴリズムの種類を指定する ``algorithm.name`` パラメータの値は無視されます。

参照ファイルについては前述の tutorial と同様です。

計算実行
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

最初にサンプルファイルが置いてあるフォルダに移動します(以下、本ソフトウェアをダウンロードしたディレクトリ直下にいることを仮定します)。

.. code-block::

   $ cd sample/user_program

``sxrdcalc`` をコピーします。

.. code-block::

   $ cp ../../sxrdcalc-main/sxrdcalc .

そのあとに、メインプログラムを実行します。(計算は通常のPCで数秒程度で終わります。)

.. code-block::

   $ python3 simple.py   

実行すると、以下のような出力が表示されます。

.. code-block::

    Optimization terminated successfully.
             Current function value: 0.000106
             Iterations: 26
             Function evaluations: 53
    iteration: 26
    len(allvecs): 27
    step: 0
    allvecs[step]: [0. 0.]
    step: 1
    allvecs[step]: [0. 0.]
    step: 2
    allvecs[step]: [0. 0.]
    (略)

``z1``, ``z2`` に各ステップでの候補パラメータと、その時の ``R-factor`` が出力されます。
最終的に推定されたパラメータは ``output/res.dat`` に出力されます。今の場合は

.. code-block::

   fx = 0.000106
   z1 = -2.351035891479114e-05
   z2 = 0.025129315870799473

となります。リファレンス ref.dat が再現されていることが分かります。
