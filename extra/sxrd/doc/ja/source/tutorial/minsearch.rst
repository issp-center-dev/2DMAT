Nelder-Mead法による最適化
====================================

ここでは、Nelder-Mead法を用いて回折データから原子座標を解析する逆問題の計算を行う方法について説明します。
具体的な計算手順は以下の通りです。

1. 参照ファイルの準備

   合わせたい参照ファイル (今回は後述する ``sic111-r3xr3_f.dat`` に相当)を準備する。

2. バルクデータの準備

   バルク部分のデータ (今回の例では ``sic111-r3xr3.blk`` に相当)を準備する。

3. メインプログラムの実行

   ``py2dmat-sxrd`` を用いて計算を実行し原子座標を推定する。

メインプログラムでは、Nelder-Mead法 (`scipy.optimize.minimize <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html>`_ を使用)を用いて、ソルバー(今回は ``sxrdcalc`` )を用いて得られた強度と、参照ファイル(``sic111-r3xr3_f.dat``)に記載された強度のずれ(R値)を最小化するパラメータを探索します。

サンプルファイルの場所
~~~~~~~~~~~~~~~~~~~~~~~~

サンプルファイルは ``sample/minsearch`` にあります。
フォルダには以下のファイルが格納されています。

- ``input.toml``

  メインプログラムの入力ファイル

- ``sic111-r3xr3.blk``, ``sic111-r3xr3_f.dat``

  メインプログラムでの計算を進めるための参照ファイル

- ``ref_res.txt``, ``ref_SimplexData.txt``

  本チュートリアルで求めたい回答を記載したファイル

- ``prepare.sh`` , ``do.sh``

  本チュートリアルを一括計算するために準備されたスクリプト

以下、これらのファイルについて説明したあと、実際の計算結果を紹介します。

入力ファイルの説明
~~~~~~~~~~~~~~~~~~~

メインプログラム用の入力ファイル ``input.toml`` の準備をします。
``input.toml`` の詳細については入力ファイルに記載されています。
ここでは、サンプルファイルにある ``input.toml`` の中身について説明します。

.. code-block::

    [base]
    dimension = 2
    
    [solver]
    name = "sxrd"
    
    [solver.config]
    sxrd_exec_file = "sxrdcalc"
    bulk_struc_in_file = "sic111-r3xr3.blk"
    [solver.param]
    scale_factor = 1.0
    type_vector = [1, 2]
    [[solver.param.domain]]
    domain_occupancy = 1.0
      [[solver.param.domain.atom]]
        name = "Si"
        pos_center = [0.00000000, 0.00000000, 1.00000000]
        DWfactor = 0.0
        occupancy = 1.0
        displace_vector = [[1, 0.0, 0.0, 1.0]]
      [[solver.param.domain.atom]]
        name = "Si"
        pos_center = [0.33333333, 0.66666667, 1.00000000]
        DWfactor = 0.0
        occupancy = 1.0
        displace_vector = [[1, 0.0, 0.0, 1.0]]
      [[solver.param.domain.atom]]
        name = "Si"
        pos_center = [0.66666667, 0.33333333, 1.00000000]
        DWfactor = 0.0
        occupancy = 1.0
        displace_vector = [[1, 0.0, 0.0, 1.0]]
      [[solver.param.domain.atom]]
        name = "Si"
        pos_center = [0.33333333, 0.33333333, 1.20000000]
        DWfactor = 0.0
        occupancy = 1.0
        displace_vector = [[2, 0.0, 0.0, 1.0]]
    [solver.reference]
    f_in_file = "sic111-r3xr3_f.dat"
    
    [algorithm]
    name = "minsearch"
    label_list = ["z1", "z2"]
    [algorithm.param]
    min_list = [-0.2, -0.2]
    max_list = [0.2, 0.2]
    initial_list = [0.0, 0.0]


最初に ``[base]`` セクションについて説明します。

- ``dimension`` は最適化したい変数の個数です。今の場合は2つの変数の最適化を行うので、 ``2`` を指定します。後述の ``solver.config.type_vector`` の項目数と一致させます。

- ``output_dir`` は出力先のディレクトリ名です。省略した場合はプログラムを実行したディレクトリになります。
  
``[solver]`` セクションではメインプログラムの内部で使用するソルバーとその設定を指定します。

- ``name`` は使用したいソルバーの名前です。 ``sxrd`` に固定されています。

ソルバーの設定は、サブセクションの ``[solver.config]``, ``[solver.param]``, ``[solver.reference]`` で行います。

``[solver.config]`` セクションではメインプログラム内部で呼び出す ``sxrdcalc`` についてのオプションを指定します。

- ``sxrd_exec_file`` は ``sxrdcalc`` のコマンド名です。パスを指定するか、コマンド名をPATH環境変数から検索します。

- ``bulk_struc_in_file`` はバルク構造ファイルを指定します。

``[solver.param]`` セクションでは ``sxrdcalc`` への入力パラメータを指定します。項目の詳細は入出力の章を参照してください。

``[solver.reference]`` セクションでは、参照する実験データを指定します。

- ``f_in_file`` は実験データが置いてあるパスを指定します。

``[algorithm]`` セクションでは、使用するアルゴリスムとその設定をします。

- ``name`` は使用したいアルゴリズムの名前で、このチュートリアルでは、Nelder-Mead法 を用いた解析を行うので、 ``minsearch`` を指定します。

- ``label_list`` は、``value_0x`` (x=1,2,3) を出力する際につけるラベル名のリストです。

``[algorithm.param]`` セクションでは、探索するパラメータの範囲や初期値を指定します。

- ``min_list`` と ``max_list`` はそれぞれ探索範囲の最小値と最大値を指定します。

- ``initial_list`` は初期値を指定します。

ここではデフォルト値を用いるため省略しましたが、その他のパラメータ、例えばNelder-Mead法で使用する収束判定などについては、``[algorithm]`` セクションで行うことが可能です。
詳細については入出力の章をご覧ください。

計算実行
~~~~~~~~~~~~

最初にサンプルファイルが置いてあるフォルダへ移動します(以下、本ソフトウェアをダウンロードしたディレクトリ直下にいることを仮定します).

.. code-block::

    $ cd sample/minsearch

``surfcalc`` をコピーします。

.. code-block::

    $ cp ../../sxrdcalc-main/sxrdcalc .

そのあとに、メインプログラムを実行します(計算時間は通常のPCで数秒程度で終わります)。

.. code-block::

    $ py2dmat-sxrd input.toml | tee log.txt

実行すると、以下の様な出力がされます。

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
    ...

``z1``, ``z2`` に各ステップでの候補パラメータと、その時の ``R-factor`` が出力されます。
最終的に推定されたパラメータは、 ``output/res.dat`` に出力されます。今の場合、

.. code-block::

    fx = 0.000106
    z1 = -2.351035891479114e-05
    z2 = 0.025129315870799473

が得られ、正解のデータ ``ref.txt`` と同じ値が得られていることがわかります。
なお、一括計算するスクリプトとして ``do.sh`` を用意しています。
``do.sh`` では ``output/res.txt`` と ``ref.txt`` の差分も比較しています。
以下、説明は割愛しますが、その中身を掲載します。

.. code-block:: sh

  #!/bin/sh

  sh ./prepare.sh

  ./bulk.exe

  time py2dmat-sxrd input.toml | tee log.txt

  echo diff output/res.txt ref.txt
  res=0
  diff output/res.txt ref.txt || res=$?
  if [ $res -eq 0 ]; then
    echo Test PASS
    true
  else
    echo Test FAILED: res.txt and ref.txt differ
    false
  fi

