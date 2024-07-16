2DMAT-LEED のインストール
=============================

実行環境・必要なパッケージ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- python 3.6.8 以上

    - 必要なpythonパッケージ

        - tomli (>= 1.2)
        - numpy (>= 1.14)

- py2dmat version 3.0 以降

- SATLEED

  - コンパイルには Fortranコンパイラが必要

ダウンロード・インストール
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. py2dmat をインストールする

   - ソースコードからのインストール

     リポジトリから py2dmat のソースファイルを取得します。

     .. code-block:: bash

        $ git clone -b update https://github.com/issp-center-dev/2DMAT.git

     pip コマンドを実行してインストールします。

     .. code-block:: bash

        $ cd 2DMAT
        $ python3 -m pip install .

     ``--user`` オプションを付けるとローカル (``$HOME/.local``) にインストールできます。

     ``python3 -m pip install .[all]`` を実行するとオプションのパッケージも同時にインストールします。
   
2. SATLEED をインストールする

   - ``SATLEED`` のソースコードは以下の URL から取得できます。

     .. code-block:: bash

	$ wget http://www.icts.hkbu.edu.hk/VanHove_files/leed/leedsatl.zip

   - ファイルを展開し、所定の手続きに従ってコンパイルします。

     ``SATLEED`` は計算したい系の詳細によってソースコードのパラメータを適宜書き換える必要があります。 ``sample/leed`` にあるサンプルを実行する場合の書き換えとコンパイルを自動で行うスクリプト ``setup.sh`` が用意されています。

     .. code-block:: bash

	$ cd sample/mapper
	$ sh ./setup.sh

     ``setup.sh`` を実行すると、 ``leedsatl`` ディレクトリに ``satl1.exe`` と ``satl2.exe`` が作成されます。
   
3. 2DMAT-LEED をインストールする

   2DMAT-LEED のソースファイルは、現在は py2dmat のソースパッケージの extra ディレクトリ内に配置されています。1. に記述した手順に従って py2dmat のソースファイルを取得した後、 ``extra/leed`` ディレクトリ内で pip コマンドを実行してインストールします。

     .. code-block:: bash

        $ cd 2DMAT/extra/leed
        $ python3 -m pip install .

     ``--user`` オプションを付けるとローカル (``$HOME/.local``) にインストールできます。

     2DMAT-LEED のライブラリと、実行コマンド ``py2dmat-leed`` がインストールされます。

実行方法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2DMAT では順問題ソルバと逆問題解析アルゴリズムを組み合わせて解析を行います。
LEEDの解析を行うには次の2通りの方法があります。

1. このパッケージに含まれる py2dmat-leed プログラムを利用して解析を行います。ユーザは、プログラムの入力となるパラメータファルを TOML 形式で作成し、プログラムの引数に指定してコマンドを実行します。逆問題解析のアルゴリズムはパラメータで選択できます。

2. 2DMAT-LEED ライブラリと 2DMAT フレームワークを用いてプログラムを作成し、解析を行います。逆問題解析アルゴリズムは import するモジュールで選択します。プログラム中に入力データの生成を組み込むなど、柔軟な使い方ができます。

パラメータの種類やライブラリの利用方法については以降の章で説明します。


アンインストール
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2DMAT-LEED モジュールおよび 2DMAT モジュールをアンインストールするには、以下のコマンドを実行します。

.. code-block:: bash

    $ python3 -m pip uninstall py2dmat-leed py2dmat

