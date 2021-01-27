``Solver`` の定義
==================

``Solver`` クラスは ``py2dmat.solver.SolverBase`` を継承したクラスとして定義します。::

    import py2dmat

    class Solver(py2dmat.solver.SolverBase):
        pass

このクラスは少なくとも次のメソッドを定義しなければなりません。

- ``__init__(self, info: py2dmat.Info)``

    - 必ず基底クラスのコンストラクタを呼び出してください

        - ``super().__init__(info)``    
        - 基底クラスのコンストラクタでは次のインスタンス変数が設定されます

            - ``self.root_dir: pathlib.Path`` : ルートディレクトリ

                - ``info.base["root_dir"]

            - ``self.output_dir: pathlib.Path`` : 出力ファイルを書き出すディレクトリ

                - ``info.base["output_dir"]

            - ``self.proc_dir: pathlib.Path`` : プロセスごとの作業用ディレクトリ

                - ``self.output_dir / str(self.mpirank)`` で初期化されます

            - ``self.work_dir: pathlib.Path`` : ソルバーが実行されるディレクトリ

                - ``self.proc_dir`` で初期化されます

    - 入力パラメータである ``info`` から必要な設定を読み取り、保存してください

- ``default_run_scheme(self) -> str``

    - ソルバーのデフォルトの実行方法 (``run_scheme``) を返してください。現在の選択肢は次のとおりです

        - ``subprocess`` : ``subprocess.run`` を用いてサブプロセス実行する
        - ``function`` : python の関数として実行する

    - 将来的に、ひとつのソルバーが実行方法をサポートできるようになる予定です

- ``prepare(self, message: py2dmat.Message) -> None``

    - ソルバーが実行される前によびだされます
    - ``message`` には入力パラメータが含まれるので、ソルバーが利用できる形に変換してください

        - 例：ソルバーの入力ファイルを生成する

- ``get_results(self) -> float``

    - ソルバーが実行されたあとに呼び出されます
    - ソルバーの実行結果を返却してください

        - 例：ソルバーの出力ファイルから実行結果を読み取る

また、次のメソッドのうち、どちらか必要な方を定義してください。

- ``command(self) -> List[str]``

    - ソルバーを実行するためのコマンド
    - ``run_scheme == "subprocess"`` の場合に必要で、そのまま ``subprocess.run`` に渡されます

- ``function(self) -> Callable[[], None]``

    - ソルバーを実行するための python 関数
    - ``run_scheme == "function"`` の場合に必要で、そのまま実行されます
