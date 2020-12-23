Nelder-Mead法による最適化
====================================

ここでは、Nelder-Mead法を用いて回折データから原子座標を解析する逆問題の計算を行う方法について説明します。
具体的な計算手順は以下の通りです。

0. 参照ファイルの準備

   合わせたい参照ファイル (今回は後述する ``experiment.txt`` に相当)を準備する。

1. 表面構造のバルク部分に関する計算実行
   
   ``bulk.exe`` を ``sample/original/minsearch`` にコピーして計算を実行する。

2. メインプログラムの実行

   ``src/py2dmat/main.py`` を用いて計算実行し原子座標を推定する。

メインプログラムでは、
Nelder-Mead法 (`scipy.optimize.fmin <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fmin.html>`_ を使用)を用いて、
ソルバー(今回は ``surf.exe`` )を用いて得られた強度と、
参照ファイル(``experiment.txt``)に記載された強度のずれ(R値)を最小化するパラメータを探索します。

サンプルファイルの場所
~~~~~~~~~~~~~~~~~~~~~~~~

サンプルファイルは ``sample/original/minsearch`` にあります。
フォルダには以下のファイルが格納されています。

- ``bulk.txt``

  ``bulk.exe`` の入力ファイル

- ``experiment.txt`` , ``template.txt``

  メインプログラムでの計算を進めるための参照ファイル

- ``ref.dat``

  本チュートリアルで求めたい回答が可能されたファイル

- ``input.toml``

  メインプログラムの入力ファイル

- ``prepare.sh`` , ``do.sh``

  本チュートリアルを一括計算するために準備されたスクリプト

以下、これらのファイルについて説明したあと、実際の計算結果を紹介します。

参照ファイルの説明
~~~~~~~~~~~~~~~~~~~

``template.txt`` , ``experiment.txt`` については ``surf.exe`` の入力ファイルとほぼ同じ形式のファイルです。
動かすパラメータ（求めたい原子座標などの値）を「 ``value_*`` 」などの適当な文字列に書き換えられています。
以下が、 ``template.txt`` の中身です。

.. code-block::

    2                                    ,NELMS,  -------- Ge(001)-c4x2
    32,1.0,0.1                           ,Ge Z,da1,sap
    0.6,0.6,0.6                          ,BH(I),BK(I),BZ(I)
    32,1.0,0.1                           ,Ge Z,da1,sap
    0.4,0.4,0.4                          ,BH(I),BK(I),BZ(I)
    9,4,0,0,2, 2.0,-0.5,0.5               ,NSGS,msa,msb,nsa,nsb,dthick,DXS,DYS
    8                                    ,NATM
    1, 1.0, 1.34502591	1	value_01   ,IELM(I),ocr(I),X(I),Y(I),Z(I)
    1, 1.0, 0.752457792	1	value_02
    2, 1.0, 1.480003343	1.465005851	value_03
    2, 1.0, 2	1.497500418	2.281675
    2, 1.0, 1	1.5	1.991675
    2, 1.0, 0	1	0.847225
    2, 1.0, 2	1	0.807225
    2, 1.0, 1.009998328	1	0.597225
    1,1                                  ,(WDOM,I=1,NDOM)


今回の入力ファイルでは、 ``value_01``, ``value_02``, ``value_03`` を用いています。
サンプルフォルダには、原子位置が正しく推定できているかを知るための参照ファイルとして、
``ref.dat`` が置いてあります。ファイルの中身は

.. code-block::

    z1 = 5.230524973874179
    z2 = 4.370622919269477
    z3 = 3.5961444501081647

となっており、 ``value_0x`` が ``z_x`` (x=1, 2, 3)に対応しています。
``experiment.txt`` は、メインプログラムで参照に用いるファイルで、
``template.txt`` に ``ref.dat`` の入っているパラメータをいれ、
順問題のチュートリアルと同様な手順で計算して得られる ``convolution.txt`` に相当しています
(順問題のチュートリアルとは ``bulk.exe`` , ``suft.exe`` の入力ファイルが異なるのでご注意ください)。


入力ファイルの説明
~~~~~~~~~~~~~~~~~~~

ここでは、メインプログラム用の入力ファイル ``input.toml`` の準備をします。
``input.toml`` の詳細については入力ファイルに記載されています。
ここでは、サンプルファイルにある ``input.toml`` の中身について説明します。

.. code-block::

    [base]
    method = "min_search"
    dimension = 3
    label_list = ["z1", "z2", "z3"]
    string_list = ["value_01", "value_02", "value_03" ]
    [solver]
    type = "surface"
    [experiment]
    path = "experiment.txt"
    first = 1
    last = 70
    [file]
    calculated_first_line = 5
    calculated_last_line = 74
    row_number = 2

最初に ``[base]`` セクションについて説明します。

- ``method`` は手法選択するキーで、 ``min_search`` を指定することでNelder-Mead法を用いた原子座標の推定が行われます。

- ``dimension`` は最適化したい変数の個数で、今の場合は ``template.txt`` で説明したように3つの変数の最適化を行うので、``3`` を指定します。

- ``label_list`` は、``value_0x`` (x=1,2,3) を出力する際につけるラベル名のリストです。

- ``string_list`` は、 ``template.txt`` で読み込む、動かしたい変数の名前のリストです。

``[solver]`` セクションではメインプログラムの内部で使用するソルバーを指定します。
このチュートリアルでは、``surf.exe`` を用いた解析を行うので、 ``surface`` を指定します。

``[experiment]`` セクションでは、実験データの置いてある場所と読みこむ範囲を指定します。

- ``path`` は実験データが置いてあるパスを指定します。

- ``first`` は実験データファイルを読み込む最初の行数を指定します。

- ``end`` は実験データファイルを読み込む最後の行数を指定します。

``[file]`` セクションでは、メインプログラム内部で呼び出す ``surf.exe`` により得られた出力ファイルを読み込む際のオプションを指定します。

- ``calculated_first_line`` は出力ファイルを読み込む最初の行数を指定します。

- ``calculated_last_line`` は出力ファイルを読み込む最後の行数を指定します。

- ``row_number`` は出力ファイルの何列目を読み込むかを指定します。

ここではデフォルト値を用いるため省略しましたが、
Nelder-Mead法で探索するパラメータ空間の指定や収束判定のパラメータについては、``param`` セクションで行うことが可能です。
詳細については入力ファイルの章をご覧ください。

計算実行
~~~~~~~~~~~~

最初にサンプルファイルが置いてあるフォルダへ移動します(以下、本ソフトウェアをダウンロードしたディレクトリ直下にいることを仮定します).

.. code-block::

    cd sample/original/minsearch

順問題の時と同様に、``bulk.exe`` と ``surf.exe`` をコピーします。

.. code-block::

    cp ../../../src/TRHEPD/bulk.exe .
    cp ../../../src/TRHEPD/surf.exe .

最初に ``bulk.exe`` を実行し、``bulkP.b`` を作成します。

.. code-block::

    ./bulk.exe

そのあとに、メインプログラムを実行します(計算時間は通常のPCで数秒程度で終わります)。

.. code-block::

    python3 ../../../src/py2dmat/main.py input.toml | tee log.txt

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

``z1``, ``z2``, ``z3`` に各ステップでの候補パラメータと、その時の``R-factor`` が出力されます。
また各ステップでの計算結果は ``Logxxxxx`` (xxxxxにステップ数)のフォルダに出力されます。
最終的に推定されたパラメータは、``res.dat`` に出力されます。今の場合、

.. code-block::

    z1 = 5.230524973874179
    z2 = 4.370622919269477
    z3 = 3.5961444501081647

が得られ、正解のデータ ``ref.dat`` と同じ値が得られていることがわかります。
なお、一括計算するスクリプトとして ``do.sh`` を用意しています。
``do.sh`` では ``res.dat`` と ``ref.dat`` の差分も比較しています。
以下、説明は割愛しますが、その中身を掲載します。

.. code-block::

    sh ./prepare.sh

    ./bulk.exe

    time python3 ../../../src/py2dmat/main.py input.toml | tee log.txt
    tail -n3 log.txt > res.dat

    echo diff res.dat ref.dat
    res=0
    diff res.dat ref.dat || res=$?
    if [ $res -eq 0 ]; then
      echo Test PASS
      true
    else
      echo Test FAILED: res.dat and ref.dat differ
      false
    fi

計算結果の可視化
~~~~~~~~~~~~~~~~~~~

それぞれのステップでのロッキングカーブのデータは、``Logxxxxx`` (xxxxはステップ数)に ``RockingCurve.txt`` として保存されています。
このデータを可視化するツール ``draw_RC_double.py`` が準備されています。
ここでは、このツールを利用して結果を可視化します。

.. code-block::

    cp Log00000001/RockingCurve.txt RockingCurve_ini.txt
    cp Log00000017/RockingCurve.txt RockingCurve_con.txt
    cp ../../../script/draw_RC_double.py .
    python draw_RC_double.py

上記を実行することで、``RC_double_minsearch.png`` が出力されます。

.. figure:: ../img/RC_double_minsearch.pdf

    Nelder-Mead法を用いた解析。赤丸が実験値、青線が最初のステップ、緑線が最後のステップで得られたロッキングカーブを表す。

図から最後のステップでは実験値と一致していることがわかります。
