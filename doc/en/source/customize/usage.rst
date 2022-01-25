Usage
===========

The following flow solves the optimization problem.
The number of flow corresponds the comment in the program example.

1. Define your ``Algorithm`` and/or ``Solver``

   - Of course, classes that ``py2dmat`` defines are available

2. Prepare the input parameter, ``info: py2dmat.Info``

   - Make a dictionary as your favorite way

      - The below example uses a TOML formatted input file for generating a dictionary

3. Instantiate ``solver: Solver``, ``runner: py2dmat.Runner``, and ``algorithm: Algorithm``

4. Invoke ``algorithm.main()``


Example

.. code-block:: python

    import sys
    import tomli
    import py2dmat

    # (1)
    class Solver(py2dmat.solver.SolverBase):
        # Define your solver
        ...

    class Algorithm(py2dmat.algorithm.AlgorithmBase):
        # Define your algorithm
        ...
    

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

Tutorial
===========

As an example, we will explain the case of adding a new benchmark function :math:`f(x)` to the analytical solver. Here, let us add the Booth function:

.. math::

    f(x,y)  =( x+2y-7)^{2} +( 2x+y-5)^{2}.

We will edit 2DMAT/src/py2dmat/solver/analytical.py, which defines various benchmark functions used by the analytical solver. First, define the booth function as follows.

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


Also, in order to be able to use the both function according to the function name read from the input file, insert the following code in the Solver class at the appropriate position.

.. code-block:: python

    elif function_name == "booth":
            self.set_function(booth)

In this way, you can specify the both function as a benchmark function when using the analytical solver.
