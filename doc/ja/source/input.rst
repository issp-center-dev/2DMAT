入力ファイル
=====================

py2dmat は入力ファイルの形式に `TOML <https://toml.io/ja/>`_ を採用しています。
入力ファイルは次の4つのセクションから構成されます。

- ``base``

  - ``py2dmat`` 全体のパラメータを指定します。

- ``solver``

  - ``Solver`` のパラメータを指定します。

- ``algorithm``

  - ``Algorithm`` のパラメータを指定します。

- ``runner``

  - ``Runner`` のパラメータを指定します。


[``base``] セクション
************************

- ``dimension``

  形式: 整数型

  説明: 探索空間の次元（探索するパラメータの数）

- ``output_dir``

  形式: string型 (default: プログラム実行時のディレクトリ)

  説明: プログラムの実行結果を出力するディレクトリ名

[``solver``] セクション
************************

``name`` でソルバーの種類を決定します。各パラメータはソルバーごとに定義されています。

- ``name``

  形式: string型

  説明: ソルバーの名前。以下のソルバーが用意されています。

    - ``sim-trhepd-rheed`` : 反射高速(陽)電子回折(RHEED, TRHEPD)の強度計算をするためのソルバー ``sim-trhepd-rheed``

    - ``analytical`` : 解析解を与えるソルバー (主にテストに利用)


各種ソルバーの詳細および入出力ファイルは :doc:`solver/index` を参照してください。

.. _input_algorithm:

[``algorithm``] セクション
*******************************

``name`` でアルゴリズムの種類を決定します。各パラメータはアルゴリズムごとに定義されています。

- ``name``

  形式: string型

  説明: アルゴリズムの名前。以下のアルゴリズムが用意されています。

    - ``minsearch`` : Nelder-Mead法による最小値探索

    - ``mapper`` : グリッド探索

    - ``exchange`` :  レプリカ交換モンテカルロ

    - ``bayes`` :  ベイズ最適化

- ``seed``

  形式: 整数値。

  説明: 初期値のランダム生成やモンテカルロ更新などで用いる擬似乱数生成器の種を指定します。
        各MPIプロセスに対して、 ``seed + mpi_rank * seed_delta`` の値が実際の種として用いられます。
        省略した場合は `Numpy の規定の方法 <https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.default_rng>`_ で初期化されます。


- ``seed_delta``

  形式: 整数値。 (default: 314159)

  説明: 疑似乱数生成器の種について、MPI プロセスごとの値を計算する際に用いられます。
        詳しくは ``seed`` を参照してください。


各種アルゴリズムの詳細および入出力ファイルは :doc:`algorithm/index` を参照してください。


[``runner``] セクション
************************
``Algorithm`` と ``Solver`` を橋渡しする要素である ``Runner`` の設定を記述します。
サブセクションとして ``log`` を持ちます。

[``log``] セクション
^^^^^^^^^^^^^^^^^^^^^^^^
solver 呼び出しのlogging に関する設定です。

- ``filename``

  形式: 文字列 (default: "runner.log")

  説明: ログファイルの名前。

- ``interval``

  形式: 整数 (default: 0)

  説明: solver を interval 回呼ぶ毎にログが書き出されます。0以下の場合、ログ書き出しは行われません。

- ``write_result``

  形式: 真偽値 (default: false)

  説明: solver からの出力を記録するかどうか。

- ``write_input``

  形式: 真偽値 (default: false)

  説明: solver への入力を記録するかどうか。
