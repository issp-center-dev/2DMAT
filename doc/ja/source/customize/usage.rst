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


プログラム例 ::

    import sys
    import toml
    import py2dmat

    # (1)
    class Solver(py2dmat.solver.SolverBase):
        # Define your solver
        pass

    class Algorithm(py2dmat.algorithm.AlgorithmBase):
        # Define your algorithm
        pass
    

    file_name = sys.argv[1]

    # (2)
    info = py2dmat.Info(toml.load(file_name))

    # (3)
    solver = Solver(info)
    runner = py2dmat.Runner(solver)
    algorithm = Algorithm(info, runner)

    # (4)
    algorithm.main()
