py2dmat のインストール
================================

実行環境・必要なパッケージ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- python 3.6.8 以上

    - 必要なpythonパッケージ

        - tomli (>= 1.2)
        - numpy (>= 1.14)

    - Optional なパッケージ

        - mpi4py (グリッド探索利用時)
        - scipy (Nelder-Mead法利用時)
        - physbo (ベイズ最適化利用時, ver. 0.3以上)

ダウンロード・インストール
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

下記に示す方法で、 ``py2dmat`` python パッケージと ``py2dmat`` コマンドがインストールできます。

- PyPI からのインストール(推奨)

    - ``python3 -m pip install py2dmat``

        - ``--user`` オプションをつけるとローカル (``$HOME/.local``) にインストールできます

        - ``py2dmat[all]`` とすると Optional なパッケージも同時にインストールします

- ソースコードからのインストール

    1. ``git clone https://github.com/issp-center-dev/2DMAT``
    2. ``python3 -m pip install ./2DMAT``

        - ``pip`` のバージョンは 19 以上が必要です (``python3 -m pip install -U pip`` で更新可能)

- サンプルファイルのダウンロード

    - サンプルファイルはソースコードに同梱されています。
    - ``git clone https://github.com/issp-center-dev/2DMAT``


実行方法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``py2dmat`` コマンドは定義済みの最適化アルゴリズム ``Algorithm`` と順問題ソルバー ``Solver`` の組み合わせで解析を行います。

.. code-block:: bash
    
    $ py2dmat input.toml

定義済みの ``Algorithm`` については :doc:`algorithm/index` を、
``Solver`` については :doc:`solver/index` を参照してください。

2次元物質構造解析向け実験データ解析の順問題ソルバーは独立なパッケージとして提供されています。
これらの解析を行う場合は別途パッケージと必要なソフトウェアをインストールしてください。
現在は以下の順問題ソルバーが用意されています。

- 全反射高速陽電子回折 (TRHEPD) -- 2DMAT-SIM-TRHEPD-RHEED パッケージ

- 表面X線回折 (SXRD) -- 2DMAT-SXRD パッケージ

- 低速電子線回折 (LEED) -- 2DMAT-LEED パッケージ

``Algorithm`` や ``Solver`` をユーザーが準備する場合は、 ``py2dmat`` パッケージを利用します。
詳しくは :doc:`customize/index` を参照してください。

なお、 プログラムを改造する場合など、 ``py2dmat`` コマンドをインストールせずに直接実行することも可能です。
``src/py2dmat_main.py`` を利用してください。

.. code-block::

    $ py2dmat src/py2dmat_main.py input.toml


アンインストール
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2DMAT モジュールをアンインストールするには、以下のコマンドを実行します。

.. code-block:: bash

    $ python3 -m pip uninstall py2dmat
