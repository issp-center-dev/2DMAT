py2dmat のインストール
=============================

実行環境・必要なパッケージ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- python 3.6 以上

    - 必要なpythonパッケージ

        - toml
        - numpy

    - Optional なパッケージ

        - mpi4py (グリッド探索利用時)
        - scipy (Nelder-Mead法利用時)
        - physbo (ベイズ最適化利用時, ver. 0.3以上)


ダウンロード・インストール
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

下記に示す方法で、 ``py2dmat`` python パッケージと ``py2dmat`` コマンドがインストールできます。

- PyPI からのインストール（将来的に推奨）（まだ利用できません）

    - ``python3 -m pip install py2dmat``

        - ``--user`` オプションをつけるとローカル (``$HOME/.local``) にインストールできます

        - ``py2dmat[all]`` とすると Optional なパッケージも同時にインストールします

- ソースコードからのインストール（開発者むけ）

    #. ``git clone https://github.com/issp-center-dev/2DMAT``
    #. ``python3 -m pip install ./2DMAT``

        - ``pip`` のバージョンは 19 以上が必要です (``python3 -m pip install -U pip`` で更新可能)

実行方法
~~~~~~~~~~~~~
``py2dmat`` コマンドは定義済みの最適化アルゴリズム ``Algorithm`` と順問題ソルバー ``Solver`` の組み合わせで解析を行います。::
    
    $ py2dmat input.toml

定義済みの ``Algorithm``/``Solver`` および入力ファイル ``input.toml`` の仕様については :doc:`input` を参照してください。

``Algorithm`` や ``Solver`` をユーザーが準備する場合は、 ``py2dmat`` パッケージを利用します。
詳しくは :doc:`customize/index` を参照してください。

アンインストール
~~~~~~~~~~~~~~~~~~~~~~~~

（PyPI に登録後は以下が可能）

.. code-block:: bash

    $ python3 -m pip uninstall py2dmat
