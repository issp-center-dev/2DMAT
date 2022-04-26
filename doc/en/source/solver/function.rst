``function`` Solver
************************

``function`` is as ``Solver`` which uses a user-defined Python 関数 ``_f(x)`` as an objective function.

Input parameters
~~~~~~~~~~~~~~~~~~~~~

The objective function can be defined by the ``function`` parameter in the ``solver`` section.

- ``function``

  Format: string

  Description: Python function (``_f(xs: np.ndarray) -> float``)

    - Function name should be ``_f`` 
    - Takes only one argument with ``np.ndarray`` type
    - Returns one ``float``
    - ``numpy`` module is imported as ``np``

An example for :math:`f(x) = \sum_i x_i^2`::

  [solver]
  name = "function"
  function = """
  def _f(x):
    return np.sum(x**2)
  """

