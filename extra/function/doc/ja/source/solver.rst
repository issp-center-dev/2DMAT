定義済み関数
================================================================

``2DMAT-Functions`` モジュールは、探索アルゴリズムの性能評価を目的とした定義済みのベンチマーク関数 :math:`f(x)` を計算する ``Solver`` です。

それぞれの関数は 2DMAT の順問題ソルバーとして利用可能なクラスとして実装されています。
定義済みの関数は以下のとおりです。

- ``Quadratics``

    - 二次形式

      .. math::

          f(\vec{x}) = \sum_{i=1}^N x_i^2

    - 最適値は :math:`f(\vec{x}^*) = 0 \quad (\forall_i x_i^* = 0)`

- ``Rosenbrock``

    - `Rosenbrock 関数 <https://en.wikipedia.org/wiki/Rosenbrock_function>`_

    .. math::

      f(\vec{x}) = \sum_{i=1}^{N-1} \left[ 100(x_{i+1} - x_i^2)^2 + (x_i - 1)^2 \right]

    - 最適値は :math:`f(\vec{x}^*) = 0 \quad (\forall_i x_i^* = 1)`

- ``Ackley``

    - `Ackley 関数 <https://en.wikipedia.org/wiki/Ackley_function>`_

    .. math::

      f(\vec{x}) = 20 + e - 20\exp\left[-0.2\sqrt{\frac{1}{N}\sum_{i=1}^N x_i^2}\right] - \exp\left[\frac{1}{N}\cos\left(2\pi x_i\right)\right]

    - 最適値は :math:`f(\vec{x}^*) = 0 \quad (\forall_i x_i^* = 0)`

- ``Himmelblau``

    - `Himmelblau 関数 <https://en.wikipedia.org/wiki/Himmelblau%27s_function>`_

    .. math::
      
      f(x,y) = (x^2+y-11)^2 + (x+y^2-7)^2

    - 最適値は :math:`f(3,2) = f(-2.805118, 3.131312) = f(-3.779310, -3.283186) = f(3.584428, -1.848126) = 0`
