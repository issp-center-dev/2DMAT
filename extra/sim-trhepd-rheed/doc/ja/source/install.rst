2DMAT-SIM-TRHEPD-RHEED のインストール
================================================================

実行環境・必要なパッケージ
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- python 3.6.8 以上

    - 必要なpythonパッケージ

        - tomli (>= 1.2)
        - numpy (>= 1.14)

- py2dmat version 3.0 以降

- sim-trhepd-rheed version 1.0.2 以降


ダウンロード・インストール
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
	  
2. sim-trhepd-rheed をインストールする

   - 公式サイトからソースパッケージをダウンロードします。

     https://github.com/sim-trhepd-rheed/sim-trhepd-rheed/releases/tag/v1.0.2
     
     .. code-block:: bash

	$ wget -O sim-trhepd-rheed-1.0.2.tar.gz https://github.com/sim-trhepd-rheed/sim-trhepd-rheed/archive/refs/tags/v1.0.2.tar.gz

   - ソースパッケージを展開し、コンパイルします。必要に応じて sim-trhepd-rheed/src 内の Makefile を編集してください。
	
     .. code-block:: bash

	$ tar xvfz sim-trhepd-rheed-1.0.2.tar.gz
	$ cd sim-trhepd-rheed-1.0.2/src
	$ make

     実行形式 ``bulk.exe``, ``surf.exe``, ``potcalc.exe``, ``xyz.exe`` が作成されます。
     ``bulk.exe`` と ``surf.exe`` を PATH の通ったディレクトリ (環境変数 PATH に列挙された、実行プログラムを探索するディレクトリ) に配置するか、実行時にディレクトリ名をつけて指定します。

3. 2dmat-sim-trhepd-rheed をインストールする

   - ソースコードからのインストール

     2dmat-sim-trhepd-rheed のソースファイルは、現在は py2dmat のソースパッケージの extra ディレクトリ内に配置されています。1. に記述した手順に従って py2dmat のソースファイルを取得した後、 ``extra/sim-trhepd-rheed`` ディレクトリ内で pip コマンドを実行してインストールします。

     .. code-block:: bash

	$ cd 2DMAT/extra/sim-trhepd-rheed
	$ python3 -m pip install .

     ``--user`` オプションを付けるとローカル (``$HOME/.local``) にインストールできます。
	    
     2DMAT-SIM-TRHEPD-RHEED のライブラリと、実行コマンド ``py2dmat-sim-trhepd-rheed`` がインストールされます。


実行方法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2DMAT では順問題ソルバと逆問題解析アルゴリズムを組み合わせて解析を行います。
TRHEPDの解析を行うには次の2通りの方法があります。

1. このパッケージに含まれる py2dmat-sim-trhepd-rheed プログラムを利用して解析を行います。ユーザは、プログラムの入力となるパラメータファルを TOML 形式で作成し、プログラムの引数に指定してコマンドを実行します。逆問題解析のアルゴリズムはパラメータで選択できます。

2. 2DMAT-SIM-TRHEPD-RHEED ライブラリと 2DMAT フレームワークを用いてプログラムを作成し、解析を行います。逆問題解析アルゴリズムは import するモジュールで選択します。プログラム中に入力データの生成を組み込むなど、柔軟な使い方ができます。

パラメータの種類やライブラリの利用方法については以降の章で説明します。


アンインストール
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2DMAT-SIM-TRHEPD-RHEED モジュールおよび 2DMAT モジュールをアンインストールするには、以下のコマンドを実行します。

.. code-block:: bash

    $ python3 -m pip uninstall py2dmat-sim-trhepd-rheed py2dmat
