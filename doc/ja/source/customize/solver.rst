``Solver`` の定義
================================

順問題を記述する ``Solver`` は、入力変数に対して目的関数の値を返す ``evaluate`` メソッドを持つクラスとして次のように定義します。

- コンストラクタ

  コンストラクタは ``Info`` クラスのメソッドを引数としてとります。

  .. code-block:: python

     class Solver:
         def __init__(self, info: py2dmat.Info):
	     pass

  コンストラクタでは、引数で指定した info からパラメータを取得します。基本パラメータを info.base から、ソルバー固有のパラメータを info.solver からそれぞれ取り出して適宜セットします。

  ディレクトリに関する規約は次の通りです。

  - ``root_dir`` はルートディレクトリです。 ``info.base["root_dir"]`` から取得でき、 ``py2dmat`` を実行するディレクトリになります。外部プログラムやデータファイルなどを参照する際に起点として利用できます。

  - ``output_dir`` は出力ファイルを書き出すディレクトリです。 ``info.base["output_dir"]`` から取得できます。通例、MPI並列の場合は各ランクからのデータを集約した結果を出力します。

  - ``proc_dir`` はプロセスごとの作業用ディレクトリです。 ``output_dir / str(self.mpirank)`` が設定されます。
    ソルバーの ``evaluate`` メソッドは ``proc_dir`` をカレントディレクトリとして Runner から呼び出され、MPIプロセスごとの中間結果などを出力します。
    MPIを使用しない場合もランク番号を0として扱います。

  - ``work_dir`` はソルバーの作業ディレクトリです。ソルバーごとに独自に規定して使用します。

    
- ``evaluate`` メソッド  

  .. code-block:: python

         def evaluate(self, x, args=(), nprocs=1, nthreads=1) -> float:
	     pass

  入力変数に対して目的変数の値を返すメソッドです。以下の引数を取ります。

  - ``x: np.ndarray``

    入力変数を numpy.ndarray 型の :math:`N` 次元ベクトルとして受け取ります。

  - ``args: Tuple = ()``

    Algorithm から渡される追加の引数で、step数と set番号からなる Tuple です。step数は Monte Carlo のステップ数や、グリッド探索のグリッド点のインデックスです。set番号は n巡目を表します。

  - ``nprocs: int = 1``

  - ``nthreads: int = 1``

    ソルバーを MPI並列・スレッド並列で実行する際のプロセス数・スレッド数を受け取ります。現在は ``procs=1``, ``nthreads=1`` のみ対応しています。

  ``evaluate`` メソッドは、Float 型の目的関数の値を返します。
