MPI対応のグリッド型探索コードの実行
=====================================

ここでは、mpi対応のグリッド型探索コードmapper\_mpi.pyの実行方法について記します。
基本的にはOpenMPIがインストールされたLinux, Mac環境を
想定しますが、合わせてWindowsにおける実行方法についても記載します。

minsearch.pyで用いた入力ファイルに加えて、探索グリッドを与えるデータ
MeshData.txtを準備する必要があります。
実行用のフォルダを作成し、そこに必要ファイルをコピーします。

フォルダ構造は以下のようになります。
ここで、test-mapperの名前、場所は任意です。

.. code-block:: none

   test-minsearch（任意のフォルダ名）
   ┣ bulk.exe
   ┣ surf.exe
   ┣ mapper_mpi.py
   ┣ bulk.txt
   ┣ template.txt
   ┣ experiment.txt
   ┗ MeshData.txt

*Linux, Macの場合*

.. code-block:: none

   mkdir test-mapper
   cd test-mapper
   cp ../source/bulk.exe .
   cp ../source/surf.exe .
   cp ../scripts/mapper_mpi.py
   cp ../sample/Si001b.txt bulk.txt
   cp ../sample/template1.txt template.txt
   cp ../sample/experiment.txt .
   cp ../sample/MeshData.txt .

*Windowsの場合*

.. code-block:: none

   mkdir test-mapper
   cd test-mapper
   copy ..\source\bulk.exe .
   copy ..\source\surf.exe .
   copy ..\scripts\mapper_mpi.py .
   copy ..\sample\Si001b.txt bulk.txt
   copy ..\sample\template1.txt template.txt
   copy ..\sample\experiment.txt .
   copy ..\sample\MeshData.txt .

続いてmapper\_mpi.pyを実行します。

*Linux, Macの場合*

Linux, Macの場合はmpirunコマンドを用いて並列化して実行します。

.. code-block:: none

   mpirun -np 4 python mapper_mpi.py

ここで、npオプションの後ろの数字で並列化数を指定しています。
上記の例では -np 4 としているので、4並列で計算します。

*Windowsの場合*

Windows環境では並列計算に対応していないため、
minsearch.pyと同様にそのまま実行します。

.. code-block:: none

   python mapper_mpi.py

上記によって、実行フォルダの下に、mapper\*\*\*\*\*\*\*\*フォルダ（\*\*\*\*\*\*\*\*にはプロセス番号が入る）が生成され、
その下のLog\*\*\*\*\*\*\*\*フォルダにロッキングカーブ等のデータが格納されます。



