実行方法
===========

次のようなフローで最適化問題を実行できます。
プログラム例にあるコメントの番号はフローの番号に対応しています。

1. ユーザ定義クラスを作成する

   - もちろん、 ``py2dmat`` で定義済みのクラスも利用可能です

2. 入力パラメータ ``info: py2dmat.Info`` を作成する

   - プログラム例では入力ファイルとしてTOML を利用していますが、辞書をつくれれば何でも構いません

3. ``solver: Solver``, ``runner: py2dmat.Runner``, ``algorithm: Algorithm`` を作成する

4. ``algorithm.main()`` を実行する


プログラム例 

.. code-block:: python

    import sys
    import tomli
    import py2dmat

    # (1)
    class Solver(py2dmat.solver.SolverBase):
        # Define your solver
        pass

    class Algorithm(py2dmat.algorithm.AlgorithmBase):
        # Define your algorithm
        pass

    # (2)
    with open(sys.argv[1]) as f:
        inp = tomli.load(f)
    info = py2dmat.Info(inp)

    # (3)
    solver = Solver(info)
    runner = py2dmat.Runner(solver, info)
    algorithm = Algorithm(info, runner)

    # (4)
    algorithm.main()

チュートリアル
==============

例として、analyticalソルバーに、新しいベンチマーク関数 :math:`f(x)` を追加する場合について説明します。ここでは、Booth関数

.. math::

   f(x,y) =( x+2y-7)^{2} +( 2x+y-5)^{2}

を追加してみましょう。2DMAT/src/py2dmat/solver/analytical.pyにはanalyticalソルバーで使われる様々なベンチマーク関数が定義されていますので、これを編集します。まず、booth関数を以下のように定義します。

.. code-block:: python

    def booth(xs: np.ndarray) -> float:
        """Booth function

        it has one global minimum f(xs) = 0 at xs = [1,3].
        """

        if xs.shape[0] != 2:
            raise RuntimeError(
                f"ERROR: himmelblau expects d=2 input, but receives d={xs.shape[0]} one"
            )
        return (xs[0] + 2 * xs[1] - 7.0) ** 2 + (2 * xs[0] + xs[1] - 5.0) ** 2

また、入力ファイルから読み込んだ関数名に応じてbooth関数を使用出来るようにするために、Solverクラス中に以下のコードを適切な位置に挿入します。

.. code-block:: python

    elif function_name == "booth":
            self.set_function(booth)

このようにすることで、analyticalソルバーを用いる際にベンチマーク関数としてbooth関数を指定出来るようになります。
