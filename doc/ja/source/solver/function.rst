``function`` ソルバー
************************

``function`` はユーザが定義した Python 関数 ``_f(x)`` を計算する ``Solver`` です。

入力パラメータ
~~~~~~~~~~~~~~~~~~~~~~~~

``solver`` セクション以下の ``funtion`` パラメータで計算する関数を定義します。

- ``function``

  形式: string型

  説明: Python 関数定義 (``_f(xs: np.ndarray) -> float``)。

    - 関数名は ``_f`` 
    - 引数は ``np.ndarray`` 型がひとつ
    - 返り値は ``float`` ひとつ
    - ``import numpy as np`` は実行済みです

:math:`f(x) = \sum_i x_i^2` を計算する例::

  [solver]
  name = "function"
  function = """
  def _f(x):
    return np.sum(x**2)
  """

