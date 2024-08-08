Usage
================================

The following flow solves the optimization problem.
The number of flow corresponds the comment in the program example.

1. Define your ``Algorithm`` and/or ``Solver``.

   - Classes that ``py2dmat`` provides are available, of course.

2. Prepare the input parameter, ``info: py2dmat.Info``.

   - ``Info`` class has a class method to read input files in TOML format.
     It is also possible to prepare a set of parameters as a dict and to pass it to the constructor of ``Info`` class.

3. Instantiate ``solver: Solver``, ``runner: py2dmat.Runner``, and ``algorithm: Algorithm``.

4. Invoke ``algorithm.main()``.


Example:

.. code-block:: python

    import sys
    import py2dmat

    # (1)
    class Solver(py2dmat.solver.SolverBase):
        # Define your solver
        ...

    class Algorithm(py2dmat.algorithm.AlgorithmBase):
        # Define your algorithm
        ...
    

    # (2)
    input_file = sys.argv[1]
    info = py2dmat.Info.from_file(input_file)

    # (3)
    solver = Solver(info)
    runner = py2dmat.Runner(solver, info)
    algorithm = Algorithm(info, runner)

    # (4)
    algorithm.main()
